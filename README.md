# Google Auth Extractor

> Exporta tus cuentas TOTP de Google Authenticator a Ente Auth, Aegis, 2FAS o CSV.
> Export your Google Authenticator TOTP accounts to Ente Auth, Aegis, 2FAS or CSV.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ¿Por qué existe esta herramienta? / Why does this tool exist?

Google Authenticator exporta las cuentas en un formato propietario (`otpauth-migration://`) que ninguna otra app puede leer directamente. Cada código QR contiene hasta 10 cuentas. Esta herramienta decodifica esos QR y extrae las claves TOTP para importarlas donde quieras.

Google Authenticator exports accounts in a proprietary format (`otpauth-migration://`) that no other app can read directly. Each QR code holds up to 10 accounts. This tool decodes those QR codes and extracts the TOTP secrets so you can import them anywhere.

---

## Características / Features

| | |
|---|---|
| 🔗 | Pegar URL `otpauth-migration://` / Paste URL |
| 🖼️ | Subir imagen QR / Upload QR image |
| 📷 | Escanear región de pantalla con el ratón / Scan screen region with mouse |
| ➕ | Acumula cuentas entre escaneos / Accumulates accounts across scans |
| 🔁 | Deduplicación automática / Auto-deduplication |
| 📋 | Copiar Emisor, Nombre o Clave individualmente / Copy Issuer, Name or Secret individually |
| 🌐 | Interfaz en Español e Inglés / Spanish and English UI |
| 🗑️ | Borrar lista para empezar de cero / Clear list to start over |
| 💾 | Exportar a Ente Auth, Aegis, 2FAS y CSV / Export to Ente Auth, Aegis, 2FAS and CSV |
| 🔒 | 100% local — ningún dato sale del equipo / No data leaves your device |

---

## Descarga / Download

- **Windows (.exe)** — descarga `GoogleAuthExtractor.exe` en [Releases](../../releases). No requiere Python.
- **Código fuente (.py)** — ver instrucciones abajo / see instructions below.

> ⚠️ Windows Defender puede mostrar una advertencia al ejecutar el `.exe`. Es un falso positivo habitual con PyInstaller. Puedes revisar el código fuente aquí mismo.
> ⚠️ Windows Defender may show a warning when running the `.exe`. This is a common false positive with PyInstaller. You can review the full source code in this repo.

---

## Uso con Python / Using with Python

### Requisitos / Requirements

- Python 3.10+
- pip

### Instalación / Installation

```bash
git clone https://github.com/joseqwrtt/Google_auth_extractor.git
cd google-auth-extractor
pip install customtkinter pillow pyzbar mss
```

**Linux / macOS** — también necesitas la librería nativa / also need the native library:

```bash
# Ubuntu / Debian
sudo apt install libzbar0

# macOS
brew install zbar
```

### Ejecutar / Run

```bash
python google_auth_extractor.py
```

---

## Uso con el .exe / Using the .exe

1. Descarga `GoogleAuthExtractor.exe` desde [Releases](../../releases)
2. Ejecútalo directamente — no requiere Python ni ninguna instalación
3. Si Windows muestra advertencia de seguridad → **Más información → Ejecutar de todas formas**

---

## Guía paso a paso / Step-by-step guide

### Paso 1 — Exportar desde Google Authenticator / Export from Google Authenticator

1. Abre Google Authenticator en tu móvil / Open Google Authenticator on your phone
2. Menú (⋮) → **Exportar cuentas / Transfer accounts → Export accounts**
3. Selecciona las cuentas / Select the accounts
4. Aparecerá uno o varios QR (hasta 10 cuentas por QR) / One or more QR codes appear (up to 10 accounts each)

---

### Paso 2 — Importar en la app / Import into the app

Tienes 3 modos / You have 3 modes:

#### 🔗 Modo URL / URL mode
1. Escanea el QR con Google Lens o cualquier lector de QR / Scan the QR with Google Lens or any QR reader
2. Copia la URL completa que empieza por `otpauth-migration://offline?data=...`
3. Pégala en la pestaña **Pegar URL / Paste URL**
4. Pulsa **Extraer cuentas / Extract accounts**

#### 🖼️ Modo imagen / Image mode
1. Haz una captura de pantalla del QR / Take a screenshot of the QR code
2. Ve a la pestaña **Imagen QR / QR Image**
3. Pulsa **Seleccionar imagen / Select image** y elige el archivo
4. Pulsa **Leer QR y extraer / Read QR & extract**

#### 📷 Modo escaneo de pantalla / Screen scan mode
1. Muestra el QR en pantalla (móvil, web, captura) / Show the QR on screen
2. Ve a la pestaña **Escanear pantalla / Scan screen**
3. Pulsa **Seleccionar región de pantalla / Select screen region**
4. La ventana se minimiza / The window minimizes
5. Dibuja un rectángulo alrededor del QR con el ratón / Draw a rectangle around the QR with the mouse
6. Suelta — las cuentas se extraen automáticamente / Release — accounts are extracted automatically

> 💡 Si tienes más de 10 cuentas repite el proceso con cada QR. Las cuentas se van acumulando en el listado. Las duplicadas se ignoran automáticamente.
> 💡 If you have more than 10 accounts, repeat the process for each QR. Accounts accumulate in the list. Duplicates are ignored automatically.

---

### Paso 3 — Exportar / Export

Una vez que tienes todas las cuentas en el listado, pulsa el botón del formato que necesites:

Once you have all accounts listed, press the button for the format you need:

| Botón / Button | Archivo / File | Compatible con / Compatible with |
|---|---|---|
| **Ente Auth** | `.txt` | Ente Auth (Importar → Desde archivo) |
| **Aegis** | `.json` | Aegis Authenticator (Android) |
| **2FAS** | `.2fas` | 2FAS (Android / iOS) |
| **CSV** | `.csv` | Bitwarden, 1Password, Raivo y otros / and others |

---

## Compilar el .exe tú mismo / Build the .exe yourself

Si no quieres usar el `.exe` de Releases puedes compilarlo tú mismo:

If you don't want to use the Releases `.exe` you can build it yourself:

1. Pon `google_auth_extractor.py` y `build_exe.bat` en la misma carpeta / Put both files in the same folder
2. Ejecuta `build_exe.bat` / Run `build_exe.bat`
3. El resultado estará en `dist/GoogleAuthExtractor.exe`

El `.bat` instala automáticamente todas las dependencias necesarias.
The `.bat` automatically installs all required dependencies.

---

## Dependencias / Dependencies

| Paquete | Para qué / Purpose |
|---|---|
| `customtkinter` | Interfaz gráfica / UI framework |
| `pillow` | Lectura de imágenes y captura de pantalla / Image reading and screen capture |
| `pyzbar` | Decodificación de QR / QR decoding |
| `mss` | Captura multi-monitor / Multi-monitor screen capture (opcional / optional) |

---

## Seguridad / Security

- El código no hace ninguna conexión de red / The code makes no network connections
- Las claves TOTP nunca salen de tu equipo / TOTP secrets never leave your device
- Puedes auditar el código fuente completo en este repositorio / You can audit the full source code in this repository
- El `.exe` se genera con PyInstaller desde este mismo código / The `.exe` is built with PyInstaller from this same code

---

## Licencia / License

MIT — úsalo libremente, modifícalo y distribúyelo. / Use it freely, modify it and distribute it.
