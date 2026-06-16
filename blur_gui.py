#!/usr/bin/env python3
import sys, re, os, subprocess, math, json, colorsys
from datetime import datetime
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PORTABLE = "--portable" in sys.argv
if PORTABLE:
    CONFIG_DIR = SCRIPT_DIR
    SCHEDULE_FILE = os.path.join(CONFIG_DIR, ".blur-schedule")
else:
    CONFIG_DIR = os.path.expanduser("~/.config/sttm")
    SCHEDULE_FILE = os.path.expanduser("~/.blur-schedule")
CONFIG_FILE = os.path.join(CONFIG_DIR, "sttm.conf")

STYLE = """
    QPushButton {{ background: rgba({r},{g},{b},0.5); color: #fff; font-weight: bold; padding: {p}px; border: none; border-radius: 4px; }}
    QPushButton:hover {{ background: rgba({r},{g},{b},0.7); }}
"""

MSG_BOX_STYLE = """
    QMessageBox {
        background-color: rgba(20, 20, 20, 0.2);
        color: white;
        min-width: 300px;
        max-width: 350px;
    }
    QMessageBox QLabel {
        color: white;
        font-size: 13px;
        background: transparent;
        qproperty-alignment: 'AlignCenter';
        padding: 10px;
    }
    QMessageBox QPushButton {
        background-color: rgba(128, 128, 128, 0.3);
        color: white;
        font-weight: bold;
        padding: 4px 12px;
        border: 1px solid rgba(128, 128, 128, 0.4);
        border-radius: 4px;
        min-width: 50px;
        max-width: 70px;
    }
    QMessageBox QPushButton:hover {
        background-color: rgba(128, 128, 128, 0.5);
    }
"""

class WallpaperPreview(QLabel):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(250); self.setMaximumHeight(500)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("QLabel { background: transparent; border: none; color: rgba(255,255,255,0.5); }")
        self.setText("No Wallpaper Selected")
        self._pixmap = None; self._rounded = None

    def set_wallpaper(self, path):
        if path and os.path.exists(path) and not (p := QPixmap(path)).isNull():
            self._pixmap = p; self._update()
        else: self.clear()

    def _update(self):
        if not self._pixmap: return
        s = self._pixmap.scaled(self.width(), self.height(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self._rounded = QPixmap(s.size()); self._rounded.fill(Qt.GlobalColor.transparent)
        path = QPainterPath(); path.addRoundedRect(QRectF(0, 0, s.width(), s.height()), 8, 8)
        p = QPainter(self._rounded); p.setRenderHint(QPainter.RenderHint.Antialiasing); p.setClipPath(path); p.drawPixmap(0, 0, s); p.end()
        self.update()

    def clear(self): self._pixmap = None; self._rounded = None; self.setText("No Wallpaper Selected"); self.update()

    def paintEvent(self, e):
        if self._rounded:
            p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
            p.drawPixmap((self.width()-self._rounded.width())//2, (self.height()-self._rounded.height())//2, self._rounded); p.end()
        else: super().paintEvent(e)

    def resizeEvent(self, e): super().resizeEvent(e); self._update() if self._pixmap else None

class CenteredCombo(QComboBox):
    def paintEvent(self, e):
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), QColor(128,128,128,77))
        pen = p.pen(); pen.setColor(QColor(128,128,128,102)); pen.setWidth(2); p.setPen(pen)
        p.drawRoundedRect(self.rect().adjusted(1,1,-1,-1), 4, 4)
        p.setPen(QColor(255,255,255)); f = self.font(); f.setBold(True); p.setFont(f)
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.currentText()); p.end()

class BlurSwitchManager(QMainWindow):
    MODES = ["MORNING","NOON","AFTERNOON","EVENING","NIGHT"]
    HOURS = {"MORNING":6,"NOON":12,"AFTERNOON":14,"EVENING":17,"NIGHT":21}
    MODE_VARS = ["TINT","OUTLINE_COLOR_ACTIVE","OUTLINE_COLOR_INACTIVE","SHADOW_COLOR","SHADOW_COLOR_INACTIVE","WALLPAPER","FF_LOGO","FF_LOGO_COLOR","RGB"]

    def __init__(self):
        super().__init__()
        os.makedirs(CONFIG_DIR, exist_ok=True)
        self.script = self._get_script(); self.cfg = {}; self.inp = {}; self.wp = {}
        self.auto = False; self.current = None; self.custom = []; self.stack = None; self.settings = {}; self._auto_proc = None; self._apply_proc = None; self._gen_proc = None; self._watch_timer = None
        self.setWindowTitle("Stoned Theme Manager"); self.resize(800, 1080); self.setMinimumSize(800,700)
        self.setFont(QFont()); self._load(); self._detect_custom(); self._ui(); self._detect_scheduler(); self._timer_status(); self._detect_mode()
        self._watch_timer = QTimer(self)
        self._watch_timer.timeout.connect(self._poll_mode)
        self._watch_timer.start(1000)

    def _has_colors(self, mode):
        for var in ["TINT","OUTLINE_COLOR_ACTIVE","OUTLINE_COLOR_INACTIVE","SHADOW_COLOR","SHADOW_COLOR_INACTIVE"]:
            if (inp := self.inp.get(f"{mode}_{var}")) and inp.text().strip():
                return True
        return False

    def _generate_colors_from_wallpaper(self, mode, auto=False):
        if self._has_colors(mode):
            if auto:
                return
            reply = self._styled_msgbox(
                QMessageBox.Icon.NoIcon, "Replace Colors",
                "<p style='text-align:center;'>This mode already has colors defined.<br>Are you sure you want to replace them?</p>",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            ).exec()
            if reply != QMessageBox.StandardButton.Yes:
                return
        wallpaper = self.inp.get(f"{mode}_WALLPAPER", QLineEdit()).text().strip()
        if not wallpaper or not os.path.exists(wallpaper):
            msg = self._styled_msgbox(QMessageBox.Icon.Warning, "Error", "No wallpaper selected!"); msg.exec()
            return
        self._gen_mode = mode
        if self._gen_proc is not None:
            if self._gen_proc.state() != QProcess.ProcessState.NotRunning:
                return
            try:
                self._gen_proc.finished.disconnect()
                self._gen_proc.errorOccurred.disconnect()
            except TypeError:
                pass
            self._gen_proc.deleteLater()
        self._gen_proc = QProcess(self)
        self._gen_proc.finished.connect(self._on_gen_finished)
        self._gen_proc.errorOccurred.connect(lambda err: self._styled_msgbox(QMessageBox.Icon.Critical, "Error", f"matugen error: {err}").exec())
        self._gen_proc.start("matugen", ["image", "-j", "hex", "--prefer", "darkness", wallpaper])

    def _on_gen_finished(self, exit_code, exit_status):
        proc = self.sender()
        if proc is None:
            self._styled_msgbox(QMessageBox.Icon.Critical, "Error", "matugen generation failed").exec()
            return
        if exit_code != 0:
            err = bytes(proc.readAllStandardError()).decode().strip()
            self._styled_msgbox(QMessageBox.Icon.Critical, "Error", f"matugen failed:\n{err}").exec()
            return
        output = bytes(proc.readAll()).decode()
        try:
            data = json.loads(output)
            colors = {k: v["default"]["color"].lstrip("#") for k, v in data.get("colors", {}).items()}
            self._apply_generated_colors(colors, self._gen_mode)
        except Exception as e:
            self._styled_msgbox(QMessageBox.Icon.Critical, "Error", f"Failed:\n{str(e)}").exec()

    def _apply_generated_colors(self, colors, mode):
        def hex_to_rgb(h):
            if h: return f"{int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)}"
            return ""
        def hex_to_tint(h, alpha=0x50):
            if h: return f"#{alpha:02x}{h[0:2]}{h[2:4]}{h[4:6]}"
            return ""
        if "primary_container" not in colors:
            self._styled_msgbox(QMessageBox.Icon.Warning, "Warning", "Could not generate colors from this wallpaper (no primary_container in matugen output).").exec()
            return
        pc = colors["primary_container"]
        pr, pg, pb = int(pc[0:2],16), int(pc[2:4],16), int(pc[4:6],16)
        h, l, s = colorsys.rgb_to_hls(pr/255.0, pg/255.0, pb/255.0)
        s = min(s * 1.5, 1.0)
        l = min(l * 1.3, 1.0)
        br, bg, bb = [max(0, min(255, int(c * 255))) for c in colorsys.hls_to_rgb(h, l, s)]
        bpc = f"{br:02x}{bg:02x}{bb:02x}"
        self.inp[f"{mode}_TINT"].setText(hex_to_tint(bpc))
        self.inp[f"{mode}_SHADOW_COLOR"].setText(hex_to_rgb(bpc))
        self.inp[f"{mode}_OUTLINE_COLOR_ACTIVE"].setText(hex_to_rgb(bpc))
        si = s * 0.5
        li = l * 0.5
        ir, ig, ib = [max(0, min(255, int(c * 255))) for c in colorsys.hls_to_rgb(h, li, si)]
        self.inp[f"{mode}_SHADOW_COLOR_INACTIVE"].setText(f"{ir},{ig},{ib}")
        self.inp[f"{mode}_OUTLINE_COLOR_INACTIVE"].setText(f"{ir},{ig},{ib}")

    def _styled_msgbox(self, icon, title, text, buttons=QMessageBox.StandardButton.Ok, parent=None):
        msg = QMessageBox(parent or self)
        msg.setIcon(icon); msg.setWindowTitle(title); msg.setText(text); msg.setStandardButtons(buttons)
        msg.setStyleSheet(MSG_BOX_STYLE)
        msg.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        msg.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        return msg

    def _get_script(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE) as f:
                    for l in f:
                        if l.startswith("SCRIPT_PATH="): return l.strip().split("=",1)[1].strip('"\'')
            except: pass
            return self._script_error("Script is malformed")
        if PORTABLE:
            auto = os.path.join(SCRIPT_DIR, "blsw.sh")
            if os.path.exists(auto):
                with open(CONFIG_FILE,"w") as f: f.write(f'SCRIPT_PATH="{auto}"\n')
                return auto
        while True:
            msg = self._styled_msgbox(QMessageBox.Icon.Information, "Setup", "Select your blurswitch.sh script."); msg.exec()
            if p := QFileDialog.getOpenFileName(self, "Select script", os.path.expanduser("~"), "*.sh;;*")[0]:
                with open(CONFIG_FILE,"w") as f: f.write(f'SCRIPT_PATH="{p}"\n')
                return p
            self._script_error("No script detected")

    def _script_error(self, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Error")
        msg.setText(message)
        msg.setStyleSheet(MSG_BOX_STYLE)
        msg.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        msg.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        browse_btn = msg.addButton("Browse", QMessageBox.ButtonRole.AcceptRole)
        exit_btn = msg.addButton("Exit", QMessageBox.ButtonRole.RejectRole)
        msg.setDefaultButton(exit_btn)
        msg.exec()
        if msg.clickedButton() == browse_btn:
            if p := QFileDialog.getOpenFileName(self, "Select script", os.path.expanduser("~"), "*.sh;;*")[0]:
                with open(CONFIG_FILE,"w") as f: f.write(f'SCRIPT_PATH="{p}"\n')
                return p
        sys.exit(1)

    def _detect_custom(self):
        prefixes = set()
        for k in self.cfg:
            for s in [f"_{v}" for v in self.MODE_VARS]:
                if k.endswith(s) and (pf := k[:-len(s)]) not in self.MODES: prefixes.add(pf)
        self.custom = sorted(prefixes)

    def _load(self):
        if not os.path.exists(self.script): return
        with open(self.script) as f:
            self.cfg = {k:v.strip('"\'') for k,v in re.findall(r'^([A-Z0-9_]+)=(.*)$', f.read(), re.MULTILINE)}

    def _icon(self, text):
        pm = QPixmap(20,20); c = QColor()
        if text:
            try:
                if "," in text: c = QColor(*map(int, text.split(",")[:3]))
                elif text.startswith("#"):
                    h = text.lstrip("#")
                    c = QColor(int(h[-6:-4] if len(h)==8 else h[0:2],16), int(h[-4:-2] if len(h)==8 else h[2:4],16), int(h[-2:] if len(h)==8 else h[4:6],16))
            except: pass
        if not c.isValid(): c = QColor(128,128,128)
        pm.fill(c); return QIcon(pm)

    def _tint_rgb(self, mode):
        v = self.inp.get(f"{mode}_TINT", QLineEdit(self.cfg.get(f"{mode}_TINT",""))).text().strip()
        if v.startswith("#") and len(v)>=7:
            try:
                h = v.lstrip("#")
                return (int(h[2:4],16),int(h[4:6],16),int(h[6:8],16)) if len(h)==8 else (int(h[0:2],16),int(h[2:4],16),int(h[4:6],16))
            except: pass

    def _btn_style(self, r, g, b, pad=8, font_size=None):
        style = STYLE.format(r=r, g=g, b=b, p=pad)
        if font_size: style += f"font-size: {font_size}px;"
        return style

    def _update_apply_buttons(self):
        for m in self.custom:
            btn = getattr(self, f'apply_{m.lower()}', None)
            if btn: btn.setText(f"Apply {m.title()} {'(Disable Auto)' if self.auto else ''}")

    def _color_btns(self):
        if self.current and (rgb := self._tint_rgb(self.current)):
            r,g,b = rgb
            for m in self.MODES+self.custom:
                if btn := getattr(self, f'apply_{m.lower()}', None): btn.setStyleSheet(self._btn_style(r,g,b))
            self.save_btn.setStyleSheet(self._btn_style(r,g,b,12)); self.auto_btn.setStyleSheet(self._btn_style(r,g,b,12))
        else:
            for m in self.MODES+self.custom:
                if btn := getattr(self, f'apply_{m.lower()}', None): btn.setStyleSheet(self._btn_style(33,150,243))
            self.save_btn.setStyleSheet(self._btn_style(76,175,80,12)); self.auto_btn.setStyleSheet(self._btn_style(255,152,0,12))

    def _mode_by_hour(self):
        h = datetime.now().hour
        mh = sorted([(m,self.inp[f"{m}_HOUR"].value()) for m in self.MODES], key=lambda x:x[1])
        mode = mh[-1][0]
        for m,hr in mh:
            if h>=hr: mode = m
        return mode

    def _sync_ui_to_mode(self, mode):
        self.current = mode
        self._color_btns()
        self._update_apply_buttons()
        for i in range(self.combo.count()):
            if self.combo.itemText(i).upper()==self.current: self.combo.setCurrentIndex(i); break

    def _detect_mode(self):
        if os.path.exists(SCHEDULE_FILE):
            try:
                with open(SCHEDULE_FILE) as f: m = re.search(r'_MODE=(\w+)', f.read())
                if m and (mn := m.group(1).upper()) in self.MODES+self.custom:
                    self._sync_ui_to_mode(mn)
                    return
            except: pass
        self._sync_ui_to_mode(self._mode_by_hour())

    def _detect_scheduler(self):
        if os.environ.get("XDG_RUNTIME_DIR") and subprocess.run(["systemctl","--user","status"], capture_output=True).returncode == 0:
            self._scheduler = "systemd"
        elif subprocess.run(["which","crontab"], capture_output=True).returncode == 0:
            self._scheduler = "cron"
        else:
            self._scheduler = None

    def _cron_installed(self):
        if self._scheduler != "cron": return False
        r = subprocess.run(["crontab","-l"], capture_output=True, text=True)
        return "blsw.sh" in r.stdout

    def _timer_status(self):
        if self._scheduler == "systemd":
            try:
                r = subprocess.run(["systemctl","--user","is-active","blurswitch-auto.timer"], capture_output=True, text=True)
                self.auto = r.stdout.strip()=="active"
            except: self.auto = False
        elif self._scheduler == "cron":
            self.auto = self._cron_installed()
        else:
            self.auto = False
        label = "Auto Mode"
        if self.auto:
            label += " (Active)"
        else:
            label += " (Disabled)"
        self.auto_btn.setText(label)
        self._update_apply_buttons()

    def _separator(self):
        s = QFrame(); s.setFrameShape(QFrame.Shape.HLine); s.setFrameShadow(QFrame.Shadow.Sunken)
        s.setStyleSheet("QFrame { color: rgba(128,128,128,0.5); margin: 10px 0; }"); return s

    def _color_row(self, form, key, label, hex=False):
        row = QHBoxLayout(); e = QLineEdit(self.cfg.get(key,"")); self.inp[key] = e; row.addWidget(e)
        b = QPushButton(); b.setFixedSize(30,30)
        b.setStyleSheet("QPushButton { background: rgba(128,128,128,0.5); border: none; border-radius: 4px; } QPushButton:hover { background: rgba(128,128,128,0.7); }")
        b.setIcon(self._icon(e.text())); b.setIconSize(QSize(20,20))
        e.textChanged.connect(lambda t: b.setIcon(self._icon(t)))
        b.clicked.connect(lambda: self._pick_hex(e,b) if hex else self._pick_rgb(e,b)); row.addWidget(b); form.addRow(label, row)

    def _file_row(self, form, key, label, mode=None):
        row = QHBoxLayout(); e = QLineEdit(self.cfg.get(key,"")); self.inp[key] = e; row.addWidget(e)
        b = QPushButton("Browse"); b.setStyleSheet(self._btn_style(128,128,128,4))
        b.clicked.connect(lambda: self._browse_wp(e, self.wp[mode]) if mode else self._browse_file(e)); row.addWidget(b); form.addRow(label, row)

    def _pick_rgb(self, e, b):
        c = QColor()
        try:
            if "," in e.text(): c = QColor(*map(int, e.text().split(",")[:3]))
        except: pass
        if (c := QColorDialog.getColor(c)).isValid(): e.setText(f"{c.red()},{c.green()},{c.blue()}"); b.setIcon(self._icon(e.text()))

    def _pick_hex(self, e, b):
        c = QColor()
        try:
            if e.text().startswith("#") and len(e.text())>=7: c = QColor(*[int(e.text().lstrip("#")[i:i+2],16) for i in range(0,6,2)])
        except: pass
        if (c := QColorDialog.getColor(c)).isValid(): e.setText(f"#{c.red():02x}{c.green():02x}{c.blue():02x}".upper()); b.setIcon(self._icon(e.text()))

    def _pick_alpha(self, mode):
        e = self.inp[f"{mode}_TINT"]; c = QColor()
        txt = e.text().strip()
        if txt.startswith("#") and len(txt)>=7:
            try:
                h = txt.lstrip("#")
                c = QColor(int(h[2:4],16),int(h[4:6],16),int(h[6:8],16),int(h[0:2],16)) if len(h)==8 else QColor(*[int(h[i:i+2],16) for i in range(0,6,2)])
            except:
                c = QColor()
        if not c.isValid():
            self._styled_msgbox(QMessageBox.Icon.Warning, "Invalid Color", "The current Glass Tint value is not a valid color.\nPick a new one or cancel.").exec()
        if (c := QColorDialog.getColor(c if c.isValid() else QColor(), options=QColorDialog.ColorDialogOption.ShowAlphaChannel)).isValid():
            e.setText(f"#{c.alpha():02x}{c.red():02x}{c.green():02x}{c.blue():02x}".upper())

    def _browse_wp(self, e, pv, mode=None):
        if path := QFileDialog.getOpenFileName(self, "Wallpaper", os.path.expanduser("~"), "Images (*.png *.jpg *.jpeg *.bmp *.gif);;*")[0]:
            e.setText(path); pv.set_wallpaper(path)
            if mode: self._generate_colors_from_wallpaper(mode, auto=True)

    def _browse_file(self, e):
        if path := QFileDialog.getOpenFileName(self, "File", os.path.expanduser("~"), "*")[0]: e.setText(path)

    def _add_custom_mode(self):
        name, ok = QInputDialog.getText(self, "New Custom Mode", "Enter mode name:")
        if not ok or not name.strip(): return
        name = name.strip().upper().replace(" ", "_")
        if name in self.MODES or name in self.custom:
            self._styled_msgbox(QMessageBox.Icon.Warning, "Error", f"Mode '{name}' already exists!").exec(); return
        if os.path.exists(self.script):
            with open(self.script, "r") as f: content = f.read()
            section = f"""#-------------------------------------------------------------------------------------------------#
# {name} mode settings
{name}_TINT=
{name}_OUTLINE_COLOR_ACTIVE=
{name}_OUTLINE_COLOR_INACTIVE=
{name}_SHADOW_COLOR=
{name}_SHADOW_COLOR_INACTIVE=
{name}_WALLPAPER=
{name}_FF_LOGO=
{name}_FF_LOGO_COLOR=
{name}_RGB=
#-------------------------------------------------------------------------------------------------#
"""
            insert_point = content.find("#get time")
            if insert_point == -1: insert_point = content.find("h=$(date +%H)")
            if insert_point == -1: content += "\n" + section
            else: content = content[:insert_point] + section + "\n" + content[insert_point:]
            with open(self.script, "w") as f: f.write(content)
        for v in self.MODE_VARS: self.cfg[f"{name}_{v}"] = ""
        self.custom.append(name); self.custom.sort()
        self.combo.blockSignals(True); self.combo.clear()
        for m in self.MODES + self.custom: self.combo.addItem(m.title(), m)
        if (ni := self.combo.findText(name.title())) >= 0: self.combo.setCurrentIndex(ni)
        self.combo.blockSignals(False)
        pg = self._mode_page(name); self.settings[name] = pg; self.stack.addWidget(pg); self.stack.setCurrentWidget(pg)
        self._update_apply_buttons()

    def _remove_custom_mode(self):
        idx = self.combo.currentIndex()
        if idx < 0: return
        mode = self.combo.itemData(idx)
        if mode not in self.custom:
            self._styled_msgbox(QMessageBox.Icon.Warning, "Error", "Only custom modes can be removed!").exec(); return
        reply = self._styled_msgbox(
            QMessageBox.Icon.NoIcon, "Remove Mode",
            "<p style='text-align:center;'>Are you sure?</p>",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ).exec()
        if reply != QMessageBox.StandardButton.Yes: return
        if os.path.exists(self.script):
            with open(self.script, "r") as f: lines = f.readlines()
            new_lines = []; skip = False
            for line in lines:
                if line.strip().startswith(f"# {mode} mode settings"):
                    if new_lines and new_lines[-1].strip().startswith("#---"):
                        new_lines.pop()
                    skip = True; continue
                if skip:
                    if not line.strip().startswith(f"{mode}_") and not line.strip().startswith("#---"):
                        skip = False; new_lines.append(line)
                    continue
                if not line.strip().startswith(f"{mode}_"): new_lines.append(line)
            with open(self.script, "w") as f: f.writelines(new_lines)
        if self.current == mode: self.current = None
        self.custom.remove(mode); self.stack.removeWidget(self.settings[mode]); del self.settings[mode]
        for v in self.MODE_VARS:
            key = f"{mode}_{v}"
            if key in self.inp: del self.inp[key]
            if key in self.cfg: del self.cfg[key]
        if mode in self.wp: del self.wp[mode]
        if hasattr(self, f'apply_{mode.lower()}'): delattr(self, f'apply_{mode.lower()}')
        self.combo.blockSignals(True); self.combo.clear()
        for m in self.MODES + self.custom: self.combo.addItem(m.title(), m)
        self.combo.setCurrentIndex(0); self.combo.blockSignals(False)
        self._update_apply_buttons()
        if not self.current: self._detect_mode()

    def _mode_page(self, mode):
        w = QWidget(); l = QVBoxLayout(w); l.setContentsMargins(10, 10, 10, 10)
        ag = QGroupBox("Appearance"); af = QFormLayout()
        pv = WallpaperPreview(); self.wp[mode] = pv
        if wp := self.cfg.get(f"{mode}_WALLPAPER",""): pv.set_wallpaper(wp)
        vc = QVBoxLayout(); vc.addWidget(pv)
        we = QLineEdit(wp); self.inp[f"{mode}_WALLPAPER"] = we
        wr = QHBoxLayout(); wr.addWidget(we)
        wb = QPushButton("Browse"); wb.setStyleSheet(self._btn_style(128,128,128,4))
        wb.clicked.connect(lambda _,e=we,p=pv,m=mode: self._browse_wp(e,p,m)); wr.addWidget(wb)
        gen_btn = QPushButton("Generate Colors")
        gen_btn.setStyleSheet(self._btn_style(128, 128, 128, 4))
        gen_btn.clicked.connect(lambda _,m=mode: self._generate_colors_from_wallpaper(m))
        wr.addWidget(gen_btn)
        vc.addLayout(wr)
        af.addRow("Wallpaper:", vc)
        tr = QHBoxLayout(); te = QLineEdit(self.cfg.get(f"{mode}_TINT","")); self.inp[f"{mode}_TINT"] = te; tr.addWidget(te)
        tb = QPushButton(); tb.setFixedSize(30,30); tb.setStyleSheet("QPushButton { background: rgba(128,128,128,0.5); border: none; border-radius: 4px; } QPushButton:hover { background: rgba(128,128,128,0.7); }")
        tb.setIcon(self._icon(te.text())); tb.setIconSize(QSize(20,20))
        te.textChanged.connect(lambda t: tb.setIcon(self._icon(t)))
        tb.clicked.connect(lambda _,m=mode: self._pick_alpha(m)); tr.addWidget(tb); af.addRow("Glass Tint:", tr)
        for k,lb in [(f"{mode}_OUTLINE_COLOR_ACTIVE","Outline Active:"),(f"{mode}_OUTLINE_COLOR_INACTIVE","Outline Inactive:"),
                     (f"{mode}_SHADOW_COLOR","Shadow Active:"),(f"{mode}_SHADOW_COLOR_INACTIVE","Shadow Inactive:")]:
            self._color_row(af, k, lb)
        ag.setLayout(af); l.addWidget(ag); l.addWidget(self._separator())
        fg = QGroupBox("Fastfetch"); ff = QFormLayout()
        self._file_row(ff, f"{mode}_FF_LOGO", "Logo File:"); self._color_row(ff, f"{mode}_FF_LOGO_COLOR", "Logo Color:", True)
        fg.setLayout(ff); l.addWidget(fg); l.addWidget(self._separator())
        sg = QGroupBox("System"); sf = QFormLayout(); sr = QHBoxLayout()
        re = QLineEdit(self.cfg.get(f"{mode}_RGB","")); self.inp[f"{mode}_RGB"] = re; sr.addWidget(re); sf.addRow("OpenRGB Profile:", sr)
        sg.setLayout(sf); l.addWidget(sg); l.addSpacing(10)
        btn_row = QHBoxLayout()
        ab = QPushButton(f"Apply {mode.title()}")
        setattr(self, f'apply_{mode.lower()}', ab)
        ab.clicked.connect(lambda _,m=mode.lower(): self._apply(m))
        btn_row.addWidget(ab, 1)
        if mode in self.custom:
            remove_btn = QPushButton()
            remove_btn.setFixedSize(35, 35)
            remove_btn.setToolTip("Remove mode")
            remove_btn.setStyleSheet(self._btn_style(220, 20, 60, 4))
            remove_btn.clicked.connect(self._remove_custom_mode)
            icon_pixmap = QPixmap(24, 24)
            icon_pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(icon_pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            pen = QPen(QColor(255, 255, 255), 3.5)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QPointF(12, 12), 8.5, 8.5)
            r = 7.5; cx, cy = 12, 12
            angle = math.pi / 4
            dx = r * math.cos(angle); dy = r * math.sin(angle)
            painter.drawLine(QPointF(cx - dx, cy - dy), QPointF(cx + dx, cy + dy))
            painter.end()
            remove_btn.setIcon(QIcon(icon_pixmap))
            remove_btn.setIconSize(QSize(24, 24))
            btn_row.addWidget(remove_btn)
        l.addLayout(btn_row)
        l.addStretch()
        return w

    def _ui(self):
        c = QWidget(); self.setCentralWidget(c); l = QVBoxLayout(c)
        tg = QGroupBox("Time Schedule (24-Hour Format)"); tl = QHBoxLayout()
        for mode in self.MODES:
            vb = QVBoxLayout(); lb = QLabel(f"{mode.title()}:"); lb.setAlignment(Qt.AlignmentFlag.AlignCenter); vb.addWidget(lb)
            sp = QSpinBox(); sp.setRange(0,23); sp.setValue(int(self.cfg.get(f"{mode}_HOUR", self.HOURS[mode]))); sp.setMinimumWidth(80)
            self.inp[f"{mode}_HOUR"] = sp; vb.addWidget(sp); tl.addLayout(vb)
        tg.setLayout(tl); l.addWidget(tg)
        mode_row = QHBoxLayout(); mode_row.addStretch()
        self.combo = CenteredCombo()
        for m in self.MODES+self.custom: self.combo.addItem(m.title(), m)
        self.combo.currentIndexChanged.connect(self._on_combo_changed)
        mode_row.addWidget(self.combo)
        add_btn = QPushButton("+"); add_btn.setFixedSize(35,35); add_btn.setStyleSheet(self._btn_style(76,175,80,4))
        add_btn.setToolTip("Add new custom mode"); add_btn.clicked.connect(self._add_custom_mode); mode_row.addWidget(add_btn)
        mode_row.addStretch(); l.addLayout(mode_row)
        self.stack = QStackedWidget()
        for m in self.MODES+self.custom:
            pg = self._mode_page(m); self.settings[m] = pg; self.stack.addWidget(pg)
        sc = QScrollArea(); sc.setWidgetResizable(True); sc.setWidget(self.stack); l.addWidget(sc)
        bl = QHBoxLayout()
        self.save_btn = QPushButton("Save Settings"); self.save_btn.clicked.connect(self._save)
        self.auto_btn = QPushButton("Auto Mode (Disabled)"); self.auto_btn.clicked.connect(self._toggle_auto)
        bl.addWidget(self.save_btn); bl.addWidget(self.auto_btn); l.addLayout(bl)

    def _on_combo_changed(self, i):
        if i < 0: return
        mode = self.combo.itemData(i)
        if mode in self.settings:
            self.current = mode
            self.stack.setCurrentWidget(self.settings[mode])

    def _toggle_auto(self):
        if self.auto: self._stop_auto()
        else: self._start_auto()
        self._update_apply_buttons()

    def _setup_auto_timer(self):
        self._save()
        if self._scheduler == "systemd":
            script_escaped = self.script.replace("\\", "\\\\").replace("\"", "\\\"")
            env = ""
            for var in ["DISPLAY", "WAYLAND_DISPLAY", "XAUTHORITY"]:
                if val := os.environ.get(var):
                    env += f"Environment={var}={val}\n"
            svc = (
                "[Unit]\nDescription=BlurSwitch Auto Mode\nAfter=graphical-session.target\n\n"
                "[Service]\nType=oneshot\n"
                f"ExecStart=\"{script_escaped}\" auto\n"
                f"{env}"
                "[Install]\nWantedBy=default.target"
            )
            tmr = "[Unit]\nDescription=BlurSwitch Auto Mode Timer\n\n[Timer]\nOnCalendar=hourly\nPersistent=true\n\n[Install]\nWantedBy=timers.target"
            d = os.path.expanduser("~/.config/systemd/user"); os.makedirs(d, exist_ok=True)
            for n,c in [("blurswitch-auto.service",svc),("blurswitch-auto.timer",tmr)]:
                with open(os.path.join(d,n),"w") as f: f.write(c)
            for cmd in [["systemctl","--user","daemon-reload"],["systemctl","--user","enable","blurswitch-auto.timer"],["systemctl","--user","start","blurswitch-auto.timer"]]:
                subprocess.run(cmd, check=True)
            linger = subprocess.run(["loginctl","show-user",os.environ.get("USER",""),"--property=Linger"], capture_output=True, text=True)
            if linger.stdout.strip() != "Linger=yes":
                reply = self._styled_msgbox(
                    QMessageBox.Icon.Question, "Enable Linger",
                    "Auto mode requires lingering to run the timer even after logout.\nEnable it?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                ).exec()
                if reply == QMessageBox.StandardButton.Yes:
                    subprocess.run(["loginctl","enable-linger"], capture_output=True)
        elif self._scheduler == "cron":
            cron_line = f"0 * * * * \"{self.script}\" auto"
            r = subprocess.run(["crontab","-l"], capture_output=True, text=True)
            existing = r.stdout
            if "blsw.sh" not in existing:
                if existing and not existing.endswith("\n"):
                    existing += "\n"
                existing += cron_line + "\n"
                p = subprocess.run(["crontab","-"], input=existing, capture_output=True, text=True)
                if p.returncode != 0: raise Exception(p.stderr.strip())
        else:
            raise Exception("No scheduler available")

    def _start_auto(self):
        if self._auto_proc is not None:
            if self._auto_proc.state() != QProcess.ProcessState.NotRunning:
                return
            try:
                self._auto_proc.finished.disconnect()
                self._auto_proc.errorOccurred.disconnect()
            except TypeError:
                pass
            self._auto_proc.deleteLater()
            self._auto_proc = None
        self.auto = True
        self.auto_btn.setText("Auto Mode (Active)")
        self._sync_ui_to_mode(self._mode_by_hour())
        try:
            self._setup_auto_timer()
        except Exception as e:
            self.auto = False
            self.auto_btn.setText("Auto Mode (Disabled)")
            self._styled_msgbox(QMessageBox.Icon.Critical, "Error", f"Failed to set up auto mode:\n{str(e)}").exec()
            return
        self._sync_ui_to_mode(self._mode_by_hour())
        self._auto_proc = QProcess(self)
        self._auto_proc.finished.connect(self._on_auto_finished)
        self._auto_proc.errorOccurred.connect(self._on_auto_error)
        self._auto_proc.start(self.script, ["auto"])

    def _on_auto_finished(self, exit_code, exit_status):
        if exit_code != 0:
            proc = self.sender()
            err = bytes(proc.readAllStandardError()).decode().strip() if proc else ""
            self._styled_msgbox(QMessageBox.Icon.Warning, "Warning", f"Auto script exited with code {exit_code}:\n{err}").exec()
        self._detect_mode()

    def _on_auto_error(self, error):
        proc = self.sender()
        err = proc.errorString() if proc else str(error)
        self._styled_msgbox(QMessageBox.Icon.Warning, "Warning", f"Immediate auto script run failed:\n{err}\n\nThe timer will retry on the next hour.").exec()

    def _poll_mode(self):
        if not os.path.exists(SCHEDULE_FILE):
            return
        try:
            with open(SCHEDULE_FILE) as f: m = re.search(r'_MODE=(\w+)', f.read())
            if m and (mn := m.group(1).upper()) in self.MODES+self.custom and mn != self.current:
                self.current = mn
                self._color_btns()
        except:
            pass

    def _stop_auto(self):
        try:
            if self._scheduler == "systemd":
                for cmd in [["systemctl","--user","stop","blurswitch-auto.timer"],["systemctl","--user","disable","blurswitch-auto.timer"]]:
                    subprocess.run(cmd)
            elif self._scheduler == "cron":
                r = subprocess.run(["crontab","-l"], capture_output=True, text=True)
                lines = [l for l in r.stdout.splitlines() if "blsw.sh" not in l]
                new = "\n".join(lines) + ("\n" if lines else "")
                subprocess.run(["crontab","-"], input=new, capture_output=True, text=True)
        except Exception as e:
            self._styled_msgbox(QMessageBox.Icon.Critical, "Error", f"Failed to stop auto mode:\n{str(e)}").exec()
        finally:
            self.auto = False
            self.auto_btn.setText("Auto Mode (Disabled)")
            if self._auto_proc is not None:
                try:
                    self._auto_proc.finished.disconnect()
                    self._auto_proc.errorOccurred.disconnect()
                except TypeError:
                    pass
                self._auto_proc.terminate()
                self._auto_proc.deleteLater()
                self._auto_proc = None

    def _save(self):
        if not os.path.exists(self.script): return
        with open(self.script) as f: lines = f.readlines()
        for k,w in self.inp.items():
            v = str(w.value()) if isinstance(w,QSpinBox) else w.text().strip()
            if not v:
                v = ""
            else:
                v = v.replace("\\", "\\\\").replace('"', '\\"').replace("$", "\\$").replace("`", "\\`")
            for i,l in enumerate(lines):
                if l.startswith(f"{k}="): lines[i] = f'{k}="{v}"\n'; break
        with open(self.script,"w") as f: f.writelines(lines)

    def _apply(self, mode):
        try:
            self._save()
            mode_upper = mode.upper()
            all_empty = all(
                not (w := self.inp.get(f"{mode_upper}_{v}")) or not w.text().strip()
                for v in self.MODE_VARS
            )
            if all_empty:
                self._styled_msgbox(QMessageBox.Icon.Information, "Nothing to change",
                    f"Mode '{mode}' has no settings configured.").exec()
                return
            for m in self.custom:
                if m.lower() == mode and self.auto:
                    self._stop_auto(); self._update_apply_buttons(); break
            for m in self.MODES + self.custom:
                if m.lower() == mode:
                    self._sync_ui_to_mode(m)
                    with open(SCHEDULE_FILE, "w") as f:
                        f.write(f"_MODE={m}\n")
                    break
        except Exception as e:
            import traceback
            self._styled_msgbox(QMessageBox.Icon.Critical, "Crash in _apply", f"{type(e).__name__}: {e}\n\n{traceback.format_exc()}").exec()
            return
        if self._apply_proc is not None:
            if self._apply_proc.state() != QProcess.ProcessState.NotRunning:
                return
            try:
                self._apply_proc.finished.disconnect()
                self._apply_proc.errorOccurred.disconnect()
            except TypeError:
                pass
            self._apply_proc.deleteLater()
        self._apply_proc = QProcess(self)
        self._apply_proc.finished.connect(self._on_apply_done)
        self._apply_proc.errorOccurred.connect(self._on_apply_error)
        self._apply_proc.start(self.script, [mode])

    def _on_apply_done(self, exit_code, exit_status):
        self._color_btns()
        if exit_code != 0:
            proc = self.sender()
            err = bytes(proc.readAllStandardError()).decode().strip() if proc else ""
            self._styled_msgbox(QMessageBox.Icon.Critical, "Error", f"Script error:\n{err}").exec()

    def _on_apply_error(self, error):
        proc = self.sender()
        err = proc.errorString() if proc else str(error)
        self._styled_msgbox(QMessageBox.Icon.Critical, "Error", f"Apply script failed:\n{err}").exec()

    def closeEvent(self, event):
        if self._watch_timer is not None:
            self._watch_timer.stop()
        for proc in [self._auto_proc, self._apply_proc, self._gen_proc]:
            if proc is not None and proc.state() != QProcess.ProcessState.NotRunning:
                proc.terminate()
                proc.waitForFinished(3000)
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QToolTip {
            background-color: rgba(20, 20, 20, 0.2);
            color: white;
            border: 1px solid rgba(128, 128, 128, 0.3);
            padding: 4px;
            border-radius: 4px;
        }
    """)
    w = BlurSwitchManager(); w.show()
    sys.exit(app.exec())
