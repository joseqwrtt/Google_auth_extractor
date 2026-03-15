#!/usr/bin/env python3
"""
Google Authenticator → Ente Auth / Aegis / 2FAS / CSV
Idiomas: Español / English
"""

import base64
import csv
import json
import threading
import urllib.parse
import uuid
from tkinter import filedialog, messagebox
import tkinter as tk

try:
    import customtkinter as ctk
except ImportError:
    raise SystemExit("pip install customtkinter")

try:
    from PIL import Image, ImageGrab, ImageTk
    PIL_OK = True
except ImportError:
    PIL_OK = False

try:
    from pyzbar.pyzbar import decode as zbar_decode
    ZBAR_OK = True
except ImportError:
    ZBAR_OK = False

try:
    import mss
    MSS_OK = True
except ImportError:
    MSS_OK = False

try:
    import cv2
    import numpy as np
    CV2_OK = True
except ImportError:
    CV2_OK = False


# ── Tema ───────────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG      = "#1a1a2e"
SURFACE = "#16213e"
CARD    = "#0f3460"
CARD2   = "#122040"
ACCENT  = "#4f8ef7"
ACCENT2 = "#7c5cbf"
TEXT    = "#e0e0e0"
MUTED   = "#7a7a9a"
SUCCESS = "#2ecc71"
WARN    = "#e67e22"
DANGER  = "#e74c3c"
BORDER  = "#2a2a4a"


# ── Traducciones ───────────────────────────────────────────────────────────────

STRINGS = {
    "es": {
        "title":            "Google Auth Extractor",
        "subtitle":         "Exporta tus cuentas TOTP a cualquier gestor",
        "tab_url":          "Pegar URL",
        "tab_file":         "Imagen QR",
        "tab_scan":         "Escanear pantalla",
        "btn_extract":      "Extraer cuentas →",
        "btn_select_img":   "Seleccionar imagen…",
        "btn_read_qr":      "Leer QR y extraer →",
        "btn_scan_region":  "📷  Seleccionar región de pantalla",
        "btn_clear":        "✕  Borrar todo",
        "lbl_no_file":      "Ningún archivo seleccionado",
        "lbl_accounts":     "Cuentas encontradas",
        "lbl_export":       "Exportar a:",
        "scan_info":
            "1.  Muestra el QR de Google Authenticator en pantalla\n"
            "2.  Pulsa el botón  →  la app se minimiza\n"
            "3.  Dibuja un rectángulo alrededor del QR con el ratón\n"
            "4.  Las cuentas se extraen automáticamente",
        "scan_minimizing":  "Minimizando… selecciona el QR en pantalla",
        "scan_processing":  "Procesando QR…",
        "field_issuer":     "Emisor",
        "field_name":       "Nombre",
        "field_secret":     "Clave",
        "field_copy":       "Copiar",
        "field_copied":     "✓ Copiado",
        "no_name":          "Cuenta sin nombre",
        "no_accounts_empty":"No hay cuentas todavía.",
        "warn_no_file":     "Primero selecciona una imagen.",
        "warn_no_accounts": "Primero extrae las cuentas.",
        "warn_deps":
            "Necesitas:\n  pip install pillow pyzbar\n\n"
            "En Linux/Mac también:\n  sudo apt install libzbar0\n  brew install zbar",
        "err_no_qr":        "No se detectó ningún QR en la imagen.\nAsegúrate de rodear solo el QR.",
        "msg_no_results":   "No se encontraron cuentas.",
        "msg_exported":     "Guardado en:\n{}",
        "msg_added":        "+{} cuenta{} añadida{}.",
        "msg_dupes":        "({} duplicada{} ignorada{})",
        "selector_hint":    "Dibuja un rectángulo sobre el QR  •  ESC para cancelar",
        "n_accounts":       "{} cuenta{}",
        "err_deps_missing": "Faltan dependencias",
        "dlg_export_title": "Guardar — {}",
        "confirm_clear":    "¿Borrar todas las cuentas?",
        "confirm_clear_btn":"Borrar",
        "cancel":           "Cancelar",
    },
    "en": {
        "title":            "Google Auth Extractor",
        "subtitle":         "Export your TOTP accounts to any authenticator",
        "tab_url":          "Paste URL",
        "tab_file":         "QR Image",
        "tab_scan":         "Scan screen",
        "btn_extract":      "Extract accounts →",
        "btn_select_img":   "Select image…",
        "btn_read_qr":      "Read QR & extract →",
        "btn_scan_region":  "📷  Select screen region",
        "btn_clear":        "✕  Clear all",
        "lbl_no_file":      "No file selected",
        "lbl_accounts":     "Accounts found",
        "lbl_export":       "Export to:",
        "scan_info":
            "1.  Show the Google Authenticator QR on screen\n"
            "2.  Press the button  →  the app minimizes\n"
            "3.  Draw a rectangle around the QR with the mouse\n"
            "4.  Accounts are extracted automatically",
        "scan_minimizing":  "Minimizing… select the QR on screen",
        "scan_processing":  "Processing QR…",
        "field_issuer":     "Issuer",
        "field_name":       "Name",
        "field_secret":     "Secret",
        "field_copy":       "Copy",
        "field_copied":     "✓ Copied",
        "no_name":          "Unnamed account",
        "no_accounts_empty":"No accounts yet.",
        "warn_no_file":     "Please select an image first.",
        "warn_no_accounts": "Please extract accounts first.",
        "warn_deps":
            "You need:\n  pip install pillow pyzbar\n\n"
            "On Linux/Mac also:\n  sudo apt install libzbar0\n  brew install zbar",
        "err_no_qr":        "No QR code detected in the image.\nMake sure to surround only the QR.",
        "msg_no_results":   "No accounts found.",
        "msg_exported":     "Saved to:\n{}",
        "msg_added":        "+{} account{} added{}.",
        "msg_dupes":        "({} duplicate{} ignored{})",
        "selector_hint":    "Draw a rectangle over the QR code  •  ESC to cancel",
        "n_accounts":       "{} account{}",
        "err_deps_missing": "Missing dependencies",
        "dlg_export_title": "Save — {}",
        "confirm_clear":    "Clear all accounts?",
        "confirm_clear_btn":"Clear",
        "cancel":           "Cancel",
    },
}

# idioma activo (mutable, compartido globalmente)
_lang = {"current": "es"}

def t(key):
    return STRINGS[_lang["current"]].get(key, key)


# ── Captura de región de pantalla ──────────────────────────────────────────────

class RegionSelector(tk.Toplevel):
    OVERLAY_ALPHA = 160
    BORDER_COLOR  = "#4f8ef7"
    BORDER_WIDTH  = 2
    CORNER_LEN    = 14
    CORNER_WIDTH  = 4

    def __init__(self, master, on_capture):
        super().__init__(master)
        self._on_capture = on_capture
        self._start      = None
        self._items      = []

        if MSS_OK:
            import mss as _mss
            with _mss.mss() as sct:
                mon = sct.monitors[0]
                raw = sct.grab(mon)
                self._screen = Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")
        else:
            self._screen = ImageGrab.grab(all_screens=True)

        sw, sh = self._screen.width, self._screen.height

        overlay       = Image.new("RGBA", (sw, sh), (0, 0, 0, self.OVERLAY_ALPHA))
        base          = self._screen.convert("RGBA")
        self._bg_dark = Image.alpha_composite(base, overlay).convert("RGB")
        self._bg_orig = self._screen.convert("RGB")

        self.overrideredirect(True)
        self.geometry(f"{sw}x{sh}+0+0")
        self.attributes("-topmost", True)
        self.lift()
        self.focus_force()

        self.canvas = tk.Canvas(self, cursor="crosshair", highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)

        self._tk_bg = ImageTk.PhotoImage(self._bg_dark)
        self.canvas.create_image(0, 0, anchor="nw", image=self._tk_bg)

        cx = sw // 2
        hint = t("selector_hint")
        self.canvas.create_text(cx+1, 41, text=hint, fill="#000000",
            font=("Helvetica", 14, "bold"))
        self.canvas.create_text(cx,   40, text=hint, fill="#ffffff",
            font=("Helvetica", 14, "bold"))

        self.canvas.bind("<ButtonPress-1>",   self._on_press)
        self.canvas.bind("<B1-Motion>",       self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Escape>", lambda e: self.destroy())

    def _clear_selection(self):
        for item in self._items: self.canvas.delete(item)
        self._items.clear()

    def _draw_selection(self, x0, y0, x1, y1):
        self._clear_selection()
        left, top     = min(x0,x1), min(y0,y1)
        right, bottom = max(x0,x1), max(y0,y1)
        if right-left < 2 or bottom-top < 2: return

        crop   = self._bg_orig.crop((left, top, right, bottom))
        tk_img = ImageTk.PhotoImage(crop)
        self._sel_imgs = [tk_img]
        self._items.append(self.canvas.create_image(left, top, anchor="nw", image=tk_img))
        self._items.append(self.canvas.create_rectangle(
            left, top, right, bottom,
            outline=self.BORDER_COLOR, width=self.BORDER_WIDTH, fill=""))

        cl, cw, cc = self.CORNER_LEN, self.CORNER_WIDTH, self.BORDER_COLOR
        for lines in [
            [(left,right)[0], (top,bottom)[0], [(left,left+cl,top,top),(left,left,top,top+cl)]],
        ]:
            pass  # replaced below

        corners = [
            [(left,top,left+cl,top),(left,top,left,top+cl)],
            [(right,top,right-cl,top),(right,top,right,top+cl)],
            [(left,bottom,left+cl,bottom),(left,bottom,left,bottom-cl)],
            [(right,bottom,right-cl,bottom),(right,bottom,right,bottom-cl)],
        ]
        for group in corners:
            for x1c,y1c,x2c,y2c in group:
                self._items.append(self.canvas.create_line(
                    x1c,y1c,x2c,y2c, fill=cc, width=cw, capstyle="round"))

        lx = left + 6
        ly = top - 18 if top > 24 else bottom + 6
        label = f" {right-left} × {bottom-top} "
        self._items.append(self.canvas.create_text(lx+1,ly+1,text=label,anchor="nw",
            fill="#000",font=("Helvetica",11,"bold")))
        self._items.append(self.canvas.create_text(lx,ly,text=label,anchor="nw",
            fill=self.BORDER_COLOR,font=("Helvetica",11,"bold")))

    def _on_press(self, e):
        self._start = (e.x, e.y); self._clear_selection()

    def _on_drag(self, e):
        if self._start: self._draw_selection(self._start[0],self._start[1],e.x,e.y)

    def _on_release(self, e):
        if not self._start: return
        x0,y0 = self._start
        left,top     = min(x0,e.x), min(y0,e.y)
        right,bottom = max(x0,e.x), max(y0,e.y)
        self.destroy()
        if right-left < 10 or bottom-top < 10: return
        self._on_capture(self._screen.crop((left,top,right,bottom)))


# ── Protobuf decoder ───────────────────────────────────────────────────────────

def _read_varint(data, pos):
    result, shift = 0, 0
    while True:
        b = data[pos]; pos += 1
        result |= (b & 0x7F) << shift
        if not (b & 0x80): break
        shift += 7
    return result, pos

def _parse_otp_parameters(data):
    fields, pos = {}, 0
    while pos < len(data):
        tag, pos = _read_varint(data, pos)
        field, wire = tag >> 3, tag & 0x7
        if wire == 2:
            length, pos = _read_varint(data, pos)
            fields[field] = data[pos:pos+length]; pos += length
        elif wire == 0:
            val, pos = _read_varint(data, pos); fields[field] = val
        else: break
    if 1 not in fields: return None
    secret = base64.b32encode(fields[1]).decode().rstrip("=")
    dec = lambda f: fields[f].decode("utf-8", errors="replace") if f in fields and isinstance(fields[f], bytes) else ""
    return {"secret": secret, "name": dec(2), "issuer": dec(3)}

def _parse_protobuf(data):
    accounts, pos = [], 0
    while pos < len(data):
        tag, pos = _read_varint(data, pos)
        field, wire = tag >> 3, tag & 0x7
        if wire == 2:
            length, pos = _read_varint(data, pos)
            chunk = data[pos:pos+length]; pos += length
            if field == 1:
                acc = _parse_otp_parameters(chunk)
                if acc: accounts.append(acc)
        elif wire == 0: _, pos = _read_varint(data, pos)
        else: break
    return accounts

def decode_migration_url(url):
    url = url.strip()
    if not url.startswith("otpauth-migration://"):
        raise ValueError("URL must start with otpauth-migration://" if _lang["current"]=="en"
                         else "La URL debe empezar con otpauth-migration://")
    params = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    if "data" not in params:
        raise ValueError("'data' parameter not found." if _lang["current"]=="en"
                         else "No se encontró el parámetro 'data'.")
    b64 = params["data"][0]
    decoded = base64.b64decode(b64 + "=" * ((4 - len(b64) % 4) % 4))
    return _parse_protobuf(decoded)

def _qr_decode_pil(img):
    if not ZBAR_OK:
        return None
    try:
        codes = zbar_decode(img.convert("RGB"))
        return codes[0].data.decode("utf-8") if codes else None
    except Exception:
        return None

def _qr_decode_cv2(img):
    if not CV2_OK:
        return None
    try:
        arr = np.array(img.convert("RGB"))
        bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        detector = cv2.QRCodeDetector()
        data, _, _ = detector.detectAndDecode(bgr)
        return data if data else None
    except Exception:
        return None

def decode_from_pil(img):
    if not ZBAR_OK and not CV2_OK:
        raise RuntimeError(
            "pip install opencv-python\n"
            "(or: pip install pyzbar)")
    url = _qr_decode_pil(img) or _qr_decode_cv2(img)
    if not url:
        raise ValueError(t("err_no_qr"))
    return decode_migration_url(url)

def decode_qr_file(path):
    if not PIL_OK: raise RuntimeError("pip install Pillow")
    return decode_from_pil(Image.open(path))


# ── Exportadores ───────────────────────────────────────────────────────────────

def export_ente(accounts, path):
    lines = []
    for a in accounts:
        uri = f"otpauth://totp/{urllib.parse.quote(a['name'] or 'account')}?secret={a['secret']}"
        if a['issuer']: uri += f"&issuer={urllib.parse.quote(a['issuer'])}"
        lines.append(uri)
    open(path, "w", encoding="utf-8").write("\n".join(lines))

def export_aegis(accounts, path):
    entries = [{"type":"totp","uuid":str(uuid.uuid4()),"name":a["name"],"issuer":a["issuer"],
                "note":"","favorite":False,"icon":None,
                "info":{"secret":a["secret"],"algo":"SHA1","digits":6,"period":30}} for a in accounts]
    json.dump({"version":1,"header":{"slots":None,"params":None},
               "db":{"version":2,"entries":entries}},
              open(path,"w",encoding="utf-8"), ensure_ascii=False, indent=2)

def export_2fas(accounts, path):
    services = [{"secret":a["secret"],"name":a["name"],"issuer":a["issuer"],"updatedAt":0,
                 "type":"TOTP","algorithm":"SHA1","digits":6,"period":30,"otp":{},
                 "order":{"position":0},"badge":{"color":"Default"},
                 "serviceTypeID":None,"groupId":None,"iconCollection":{"id":"default"}} for a in accounts]
    json.dump({"services":services,"groups":[],"updatedAt":0,"schemaVersion":4,
               "appVersionCode":1000,"appVersionName":"1.0.0","nextTokenAt":0},
              open(path,"w",encoding="utf-8"), ensure_ascii=False, indent=2)

def export_csv(accounts, path):
    with open(path,"w",newline="",encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["issuer","name","secret","type","algorithm","digits","period","totp_uri"])
        w.writeheader()
        for a in accounts:
            uri = (f"otpauth://totp/{urllib.parse.quote(a['name'] or 'account')}"
                   f"?secret={a['secret']}&issuer={urllib.parse.quote(a['issuer'] or '')}"
                   f"&algorithm=SHA1&digits=6&period=30")
            w.writerow({"issuer":a["issuer"],"name":a["name"],"secret":a["secret"],
                        "type":"TOTP","algorithm":"SHA1","digits":6,"period":30,"totp_uri":uri})

EXPORTERS = [
    {"label":"Ente Auth",  "ext":".txt",  "fn":export_ente,  "color":ACCENT,  "default":"ente_auth_import.txt",  "ft":[("TXT","*.txt")]},
    {"label":"Aegis",      "ext":".json", "fn":export_aegis, "color":SUCCESS, "default":"aegis_import.json",     "ft":[("JSON","*.json")]},
    {"label":"2FAS",       "ext":".2fas", "fn":export_2fas,  "color":WARN,    "default":"2fas_import.2fas",      "ft":[("2FAS","*.2fas"),("JSON","*.json")]},
    {"label":"CSV",        "ext":".csv",  "fn":export_csv,   "color":ACCENT2, "default":"totp_import.csv",       "ft":[("CSV","*.csv")]},
]


# ── Tarjeta de cuenta ──────────────────────────────────────────────────────────

class AccountCard(ctk.CTkFrame):
    def __init__(self, master, account: dict, index: int, **kw):
        super().__init__(master, fg_color=CARD2, corner_radius=10,
                         border_width=1, border_color=BORDER, **kw)
        self._account = account
        self._build(index)

    def _build(self, index):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=14, pady=(10,6))
        ctk.CTkLabel(header, text=f" {index} ",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=CARD, corner_radius=5,
            text_color=MUTED, width=26, height=20).pack(side="left", padx=(0,8))
        title = self._account["name"] or self._account["issuer"] or t("no_name")
        ctk.CTkLabel(header, text=title,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEXT, anchor="w").pack(side="left", fill="x", expand=True)

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=14, pady=(0,8))

        fields = [
            (t("field_issuer"), "issuer", "#5b8dee"),
            (t("field_name"),   "name",   "#7c5cbf"),
            (t("field_secret"), "secret", "#2ecc71"),
        ]
        for label, key, color in fields:
            self._field_row(label, self._account.get(key,"") or "—", color)

        ctk.CTkFrame(self, fg_color="transparent", height=6).pack()

    def _field_row(self, label, value, color):
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=2)
        ctk.CTkLabel(row, text=label,
            font=ctk.CTkFont(size=11), text_color=MUTED,
            width=52, anchor="w").pack(side="left")
        display = value if len(value) <= 38 else value[:35]+"…"
        ctk.CTkLabel(row, text=display,
            font=ctk.CTkFont(family="Courier" if label==t("field_secret") else None, size=12),
            text_color=TEXT, anchor="w").pack(side="left", fill="x", expand=True)
        btn = ctk.CTkButton(row, text=t("field_copy"),
            width=62, height=24, corner_radius=6,
            fg_color=CARD, hover_color=color,
            text_color=MUTED, border_width=1, border_color=BORDER,
            font=ctk.CTkFont(size=11))
        btn.configure(command=lambda v=value, b=btn, c=color: self._copy(v, b, c))
        btn.pack(side="right")

    def _copy(self, value, btn, color):
        self.clipboard_clear(); self.clipboard_append(value)
        btn.configure(text=t("field_copied"), fg_color=color, text_color="#fff")
        self.after(1200, lambda: btn.configure(
            text=t("field_copy"), fg_color=CARD, text_color=MUTED))


class AccountsPanel(ctk.CTkScrollableFrame):
    def __init__(self, master, **kw):
        super().__init__(master, fg_color=BG, **kw)
        self._cards = []

    def clear(self):
        for c in self._cards: c.destroy()
        self._cards.clear()

    def set_accounts(self, accounts):
        self.clear()
        if not accounts:
            ctk.CTkLabel(self, text=t("no_accounts_empty"),
                text_color=MUTED, font=ctk.CTkFont(size=12)).pack(pady=20)
            return
        for i, acc in enumerate(accounts, 1):
            card = AccountCard(self, acc, i)
            card.pack(fill="x", pady=(0,8), padx=2)
            self._cards.append(card)


# ── App ────────────────────────────────────────────────────────────────────────

class App(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=BG)
        self.title("Google Auth Extractor")
        self.resizable(True, True)
        self._accounts  = []
        self._qr_path   = None
        self._active_tab = "url"
        self._body_frame = None
        self._build()
        self._center(660, 700)

    def _center(self, w, h):
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _darken(self, hex_color, f=0.72):
        c = hex_color.lstrip("#")
        r,g,b = int(c[0:2],16),int(c[2:4],16),int(c[4:6],16)
        return "#{:02x}{:02x}{:02x}".format(int(r*f),int(g*f),int(b*f))

    # ── Cambio de idioma ──────────────────────────────────────────────────────
    def _toggle_lang(self):
        _lang["current"] = "en" if _lang["current"] == "es" else "es"
        # Reconstruir UI completa conservando cuentas
        saved = list(self._accounts)
        saved_tab = self._active_tab
        self._hdr_subtitle.configure(text=t("subtitle"))
        self._lang_btn.configure(
            text="🌐  EN" if _lang["current"] == "es" else "🌐  ES")
        if self._body_frame:
            self._body_frame.destroy()
        self._build_body(saved_tab)
        self._accounts = saved
        self.accounts_panel.set_accounts(self._accounts)
        self._refresh_count()

    # ── Layout ────────────────────────────────────────────────────────────────
    def _build(self):
        # Header fijo
        hdr = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=0)
        hdr.pack(fill="x")
        ctk.CTkLabel(hdr, text=t("title"),
            font=ctk.CTkFont(size=17, weight="bold"), text_color=TEXT
        ).pack(side="left", padx=18, pady=13)
        self._hdr_subtitle = ctk.CTkLabel(hdr, text=t("subtitle"),
            font=ctk.CTkFont(size=11), text_color=MUTED)
        self._hdr_subtitle.pack(side="left")
        # Botón de idioma en el header
        self._lang_btn = ctk.CTkButton(hdr,
            text="🌐  EN",
            width=68, height=26, corner_radius=7,
            fg_color=CARD, text_color=MUTED,
            border_width=1, border_color=BORDER,
            hover_color=BORDER, font=ctk.CTkFont(size=11),
            command=self._toggle_lang)
        self._lang_btn.pack(side="right", padx=14)
        self._build_body("url")

    def _build_body(self, active_tab="url"):
        self._body_frame = ctk.CTkFrame(self, fg_color=BG)
        self._body_frame.pack(fill="both", expand=True, padx=14, pady=10)
        body = self._body_frame

        # ── Input card ────────────────────────────────────────────────────────
        ic = ctk.CTkFrame(body, fg_color=SURFACE, corner_radius=12)
        ic.pack(fill="x", pady=(0,8))

        tabs = ctk.CTkFrame(ic, fg_color="transparent")
        tabs.pack(fill="x", padx=14, pady=(12,8))

        self._btn_url = ctk.CTkButton(tabs, text=t("tab_url"),
            width=100, height=28, corner_radius=7,
            fg_color=CARD, text_color=MUTED, hover_color=BORDER,
            font=ctk.CTkFont(size=12),
            command=lambda: self._switch("url"))
        self._btn_url.pack(side="left", padx=(0,6))

        self._btn_file = ctk.CTkButton(tabs, text=t("tab_file"),
            width=100, height=28, corner_radius=7,
            fg_color=CARD, text_color=MUTED, hover_color=BORDER,
            font=ctk.CTkFont(size=12),
            command=lambda: self._switch("file"))
        self._btn_file.pack(side="left", padx=(0,6))

        self._btn_scan = ctk.CTkButton(tabs, text=t("tab_scan"),
            width=140, height=28, corner_radius=7,
            fg_color=CARD,
            text_color=MUTED if (PIL_OK and ZBAR_OK) else DANGER,
            hover_color=BORDER, font=ctk.CTkFont(size=12),
            command=lambda: self._switch("scan"))
        self._btn_scan.pack(side="left")

        # ── Panel URL ─────────────────────────────────────────────────────────
        self._p_url = ctk.CTkFrame(ic, fg_color="transparent")

        self.txt_url = ctk.CTkTextbox(self._p_url, height=65,
            fg_color=CARD, text_color=TEXT,
            font=ctk.CTkFont(family="Courier", size=11),
            border_width=1, border_color=BORDER, corner_radius=8)
        self.txt_url.pack(fill="x", pady=(0,8))
        self.txt_url.insert("1.0", "otpauth-migration://offline?data=")

        ctk.CTkButton(self._p_url, text=t("btn_extract"),
            height=32, corner_radius=8, width=170,
            fg_color=ACCENT, hover_color=self._darken(ACCENT),
            text_color="#fff", font=ctk.CTkFont(size=12, weight="bold"),
            command=self._process_url).pack(anchor="w")

        # ── Panel archivo QR ──────────────────────────────────────────────────
        self._p_file = ctk.CTkFrame(ic, fg_color="transparent")

        if not PIL_OK or not ZBAR_OK:
            missing = " ".join(filter(None,[
                "Pillow" if not PIL_OK else "",
                "pyzbar" if not ZBAR_OK else ""]))
            ctk.CTkLabel(self._p_file, text=f"⚠  pip install {missing}",
                text_color=WARN, font=ctk.CTkFont(size=11)).pack(anchor="w", pady=(0,4))

        self.lbl_file = ctk.CTkLabel(self._p_file,
            text=t("lbl_no_file"), text_color=MUTED, font=ctk.CTkFont(size=11))
        self.lbl_file.pack(anchor="w", pady=(0,6))

        fr = ctk.CTkFrame(self._p_file, fg_color="transparent")
        fr.pack(anchor="w", pady=(0,12))
        ctk.CTkButton(fr, text=t("btn_select_img"),
            width=155, height=32, corner_radius=8,
            fg_color=CARD, text_color=TEXT,
            border_width=1, border_color=BORDER, hover_color=BORDER,
            command=self._pick_image).pack(side="left", padx=(0,8))
        ctk.CTkButton(fr, text=t("btn_read_qr"),
            width=165, height=32, corner_radius=8,
            fg_color=ACCENT, hover_color=self._darken(ACCENT),
            text_color="#fff", font=ctk.CTkFont(size=12, weight="bold"),
            command=self._process_qr_file).pack(side="left")

        # ── Panel escanear pantalla ────────────────────────────────────────────
        self._p_scan = ctk.CTkFrame(ic, fg_color="transparent")

        if not PIL_OK or not ZBAR_OK:
            ctk.CTkLabel(self._p_scan,
                text="⚠  pip install pillow pyzbar" + (" mss" if not MSS_OK else ""),
                text_color=DANGER, font=ctk.CTkFont(size=11)).pack(anchor="w", pady=(0,6))

        info_box = ctk.CTkFrame(self._p_scan, fg_color=CARD, corner_radius=8)
        info_box.pack(fill="x", pady=(0,8))
        ctk.CTkLabel(info_box, text=t("scan_info"),
            text_color=MUTED, font=ctk.CTkFont(size=11),
            justify="left").pack(padx=12, pady=10)

        self.lbl_scan_status = ctk.CTkLabel(self._p_scan, text="",
            text_color=MUTED, font=ctk.CTkFont(size=11))
        self.lbl_scan_status.pack(anchor="w", pady=(0,4))

        ctk.CTkButton(self._p_scan, text=t("btn_scan_region"),
            height=36, corner_radius=8, width=250,
            fg_color=ACCENT2, hover_color=self._darken(ACCENT2),
            text_color="#fff", font=ctk.CTkFont(size=13, weight="bold"),
            command=self._start_region_scan).pack(anchor="w", pady=(0,12))

        # ── Panel de cuentas ──────────────────────────────────────────────────
        res_hdr = ctk.CTkFrame(body, fg_color="transparent")
        res_hdr.pack(fill="x", pady=(0,6))
        ctk.CTkLabel(res_hdr, text=t("lbl_accounts"),
            font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT).pack(side="left")
        self.lbl_count = ctk.CTkLabel(res_hdr, text="",
            font=ctk.CTkFont(size=11), text_color=MUTED)
        self.lbl_count.pack(side="left", padx=8)
        ctk.CTkButton(res_hdr, text=t("btn_clear"),
            width=105, height=24, corner_radius=6,
            fg_color="transparent", hover_color=DANGER,
            text_color=MUTED, border_width=1, border_color=BORDER,
            font=ctk.CTkFont(size=11),
            command=self._clear_accounts).pack(side="right")

        self.accounts_panel = AccountsPanel(body, height=260)
        self.accounts_panel.pack(fill="both", expand=True, pady=(0,8))

        # ── Exportar ──────────────────────────────────────────────────────────
        ec = ctk.CTkFrame(body, fg_color=SURFACE, corner_radius=12)
        ec.pack(fill="x")
        el = ctk.CTkFrame(ec, fg_color="transparent")
        el.pack(fill="x", padx=14, pady=(10,12))
        ctk.CTkLabel(el, text=t("lbl_export"),
            font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT
        ).pack(side="left", padx=(0,10))
        for cfg in EXPORTERS:
            ctk.CTkButton(el,
                text=f"↓  {cfg['label']}",
                width=115, height=30, corner_radius=8,
                fg_color=cfg["color"], hover_color=self._darken(cfg["color"]),
                text_color="#fff", font=ctk.CTkFont(size=11, weight="bold"),
                command=lambda c=cfg: self._export(c)
            ).pack(side="left", padx=(0,6))

        # Activar tab correcto
        self._switch(active_tab)

    # ── Tabs ──────────────────────────────────────────────────────────────────
    def _switch(self, tab):
        self._active_tab = tab
        for p in (self._p_url, self._p_file, self._p_scan):
            p.pack_forget()
        for btn, key in [(self._btn_url,"url"),(self._btn_file,"file"),(self._btn_scan,"scan")]:
            active = key == tab
            btn.configure(
                fg_color=ACCENT if active else CARD,
                text_color="#fff" if active else MUTED,
                font=ctk.CTkFont(size=12, weight="bold" if active else "normal"))
        panel = {"url":self._p_url, "file":self._p_file, "scan":self._p_scan}[tab]
        panel.pack(fill="x", padx=14, pady=(0,12))

    # ── Escaneo de pantalla ────────────────────────────────────────────────────
    def _start_region_scan(self):
        if not PIL_OK or not ZBAR_OK:
            messagebox.showerror(t("err_deps_missing"), t("warn_deps")); return
        self.lbl_scan_status.configure(text=t("scan_minimizing"), text_color=MUTED)
        self.after(300, self._open_selector)

    def _open_selector(self):
        self.iconify()
        self.after(400, self._launch_selector)

    def _launch_selector(self):
        def on_capture(img):
            self.after(0, self.deiconify)
            self.after(100, lambda: self._process_captured(img))
        try:
            sel = RegionSelector(self, on_capture)
            sel.wait_window()
            self.after(0, self.deiconify)
        except Exception as e:
            self.deiconify()
            messagebox.showerror("Error", str(e))

    def _process_captured(self, img):
        self.lbl_scan_status.configure(text=t("scan_processing"), text_color=MUTED)
        def task():
            try:
                accounts = decode_from_pil(img)
                self.after(0, self._show_results, accounts)
            except Exception as e:
                self.after(0, lambda: self.lbl_scan_status.configure(
                    text=f"✗ {e}", text_color=DANGER))
        threading.Thread(target=task, daemon=True).start()

    # ── Acciones ──────────────────────────────────────────────────────────────
    def _pick_image(self):
        path = filedialog.askopenfilename(
            title=t("btn_select_img"),
            filetypes=[("Images","*.png *.jpg *.jpeg *.bmp *.webp"),("All","*.*")])
        if path:
            self._qr_path = path
            self.lbl_file.configure(
                text=path if len(path)<55 else "…"+path[-52:],
                text_color=TEXT)

    def _process_url(self):
        self._run(decode_migration_url, self.txt_url.get("1.0","end").strip())

    def _process_qr_file(self):
        if not self._qr_path:
            messagebox.showwarning("", t("warn_no_file")); return
        self._run(decode_qr_file, self._qr_path)

    def _run(self, fn, arg):
        def task():
            try:
                self.after(0, self._show_results, fn(arg))
            except Exception as e:
                self.after(0, messagebox.showerror, "Error", str(e))
        threading.Thread(target=task, daemon=True).start()

    def _show_results(self, accounts):
        if not accounts:
            messagebox.showinfo("", t("msg_no_results")); return
        existing = {a["secret"] for a in self._accounts}
        new_accs = [a for a in accounts if a["secret"] not in existing]
        dupes    = len(accounts) - len(new_accs)
        self._accounts.extend(new_accs)
        self.accounts_panel.set_accounts(self._accounts)
        self._refresh_count()
        n   = len(new_accs)
        s   = "s" if n != 1 else ""
        msg = t("msg_added").format(n, s, s)
        if dupes:
            ds = "s" if dupes != 1 else ""
            msg += "\n" + t("msg_dupes").format(dupes, ds, ds)
        if hasattr(self, "lbl_scan_status"):
            self.lbl_scan_status.configure(text=msg, text_color=SUCCESS)

    def _clear_accounts(self):
        if not self._accounts: return
        self._accounts.clear()
        self.accounts_panel.set_accounts([])
        self._refresh_count()
        if hasattr(self, "lbl_scan_status"):
            self.lbl_scan_status.configure(text="", text_color=MUTED)

    def _refresh_count(self):
        n = len(self._accounts)
        s = "s" if n != 1 else ""
        self.lbl_count.configure(
            text=t("n_accounts").format(n, s) if n else "",
            text_color=SUCCESS if n else MUTED)

    def _export(self, cfg):
        if not self._accounts:
            messagebox.showwarning("", t("warn_no_accounts")); return
        path = filedialog.asksaveasfilename(
            title=t("dlg_export_title").format(cfg["label"]),
            defaultextension=cfg["ext"], filetypes=cfg["ft"],
            initialfile=cfg["default"])
        if not path: return
        try:
            cfg["fn"](self._accounts, path)
            messagebox.showinfo("", t("msg_exported").format(path))
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    app = App()
    app.mainloop()