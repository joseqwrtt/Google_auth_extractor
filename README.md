# Google Auth Extractor

> Exporta tus cuentas TOTP de Google Authenticator a TXT, Aegis, 2FAS o CSV.  
> Export your Google Authenticator TOTP accounts to TXT, Aegis, 2FAS or CSV.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ¿Por qué existe esta herramienta? / Why does this tool exist?

Google Authenticator exporta las cuentas en un formato propietario (`otpauth-migration://`) que ninguna otra app puede leer directamente. Cada código QR contiene hasta 10 cuentas. Esta herramienta decodifica esos QR y extrae las claves TOTP para que puedas importarlas donde quieras.

Google Authenticator exports accounts in a proprietary format (`otpauth-migration://`) that no other app can read directly. Each QR code holds up to 10 accounts. This tool decodes those QR codes and extracts the TOTP secrets so you can import them anywhere.

---

## Características / Features

| | |
|---|---|
| 🔗 | Pegar URL `otpauth-migration://` directamente / Paste URL directly |
| 🖼️ | Subir imagen o captura del QR / Upload QR image or screenshot |
| 📷 | Escanear región de pantalla con el ratón en tiempo real / Live screen region scanner |
| ➕ | Acumula cuentas entre escaneos (10 por QR) / Accumulates accounts across scans |
| 🔁 | Deduplicación automática / Auto-deduplication |
| 📋 | Copiar Emisor, Nombre o Clave individualmente / Copy Issuer, Name or Secret individually |
| 🌐 | Interfaz en Español e Inglés / Spanish and English UI |
| 🗑️ | Borrar lista para empezar de cero / Clear list to start over |
| 💾 | Exportar a 4 formatos / Export to 4 formats: TXT, Aegis, 2FAS, CSV |
| 🔒 | 100% local — ningún dato sale del equipo / No data leaves your device |

---

## Instalación / Installation

### 1. Clona el repositorio / Clone the repo

```bash
git clone https://github.com/joseqwrtt/Google_auth_extractor.git
cd Google_auth_extractor
```

### 2. Instala Python

Descarga e instala Python desde [https://python.org](https://python.org) (versión 3.10 o superior).

> ⚠️ **Windows**: durante la instalación marca la opción **"Add Python to PATH"**.

### 3. Instala las dependencias

Abre una terminal en la carpeta del proyecto y ejecuta:

```bash
pip install customtkinter pillow pyzbar opencv-python mss
```

> **Linux / macOS** — también necesitas la librería nativa de zbar:
> ```bash
> # Ubuntu / Debian
> sudo apt install libzbar0
>
> # macOS
> brew install zbar
> ```

---

## Uso / Usage

### Ejecutar / Run

```bash
python Google_auth_extractor.py
```

> **Windows con varias versiones de Python** — si tienes más de una versión instalada, usa la ruta completa para asegurarte:
> ```bash
> C:\Python311\python.exe Google_auth_extractor.py
> ```
> O crea un archivo `ejecutar.bat` en la misma carpeta con este contenido:
> ```bat
> python "%~dp0Google_auth_extractor.py"
> pause
> ```
> Y haz doble clic en él para arrancar.

---

## Guía paso a paso / Step-by-step guide

### Paso 1 — Exportar desde Google Authenticator

1. Abre Google Authenticator en tu móvil
2. Toca el menú (⋮) → **Exportar cuentas / Transfer accounts → Export accounts**
3. Selecciona las cuentas que quieres exportar
4. Aparecerá uno o varios QR — **máximo 10 cuentas por QR**

### Paso 2 — Importar en la app (elige un modo)

#### 🔗 Modo URL
1. Escanea el QR con **Google Lens** o cualquier lector de QR
2. Copia la URL completa que empieza por `otpauth-migration://offline?data=...`
3. Pégala en la pestaña **Pegar URL**
4. Pulsa **Extraer cuentas**

#### 🖼️ Modo imagen
1. Haz una captura de pantalla del QR en tu ordenador
2. Ve a la pestaña **Imagen QR**
3. Pulsa **Seleccionar imagen** y elige el archivo
4. Pulsa **Leer QR y extraer**

#### 📷 Modo escaneo de pantalla
1. Muestra el QR en pantalla (desde el móvil, captura, etc.)
2. Ve a la pestaña **Escanear pantalla**
3. Pulsa **Seleccionar región de pantalla**
4. La ventana se minimiza automáticamente
5. Dibuja un rectángulo alrededor del QR con el ratón
6. Al soltar, las cuentas se extraen automáticamente

> 💡 Si tienes **más de 10 cuentas**, repite el proceso con cada QR. Las cuentas se acumulan en el listado y las duplicadas se ignoran automáticamente.

### Paso 3 — Exportar

Una vez con todas las cuentas en el listado, pulsa el botón del formato que necesites:

| Botón | Archivo | Compatible con |
|---|---|---|
| **TXT** | `.txt` | TXT → Importar → Desde archivo |
| **Aegis** | `.json` | Aegis Authenticator (Android) |
| **2FAS** | `.2fas` | 2FAS (Android / iOS) |
| **CSV** | `.csv` | Bitwarden, 1Password, Raivo y otros |

---

## Dependencias / Dependencies

| Paquete | Para qué / Purpose |
|---|---|
| `customtkinter` | Interfaz gráfica / UI |
| `pillow` | Lectura de imágenes y captura / Images and screen capture |
| `pyzbar` | Decodificación de QR (principal) / QR decoding (primary) |
| `opencv-python` | Decodificación de QR (alternativa) / QR decoding (fallback) |
| `mss` | Captura multi-monitor / Multi-monitor capture (opcional) |

---

## Solución de problemas / Troubleshooting

**El escáner de pantalla no funciona / Screen scanner doesn't work**
```bash
pip install pillow pyzbar opencv-python mss
# Linux/Mac también:
sudo apt install libzbar0   # Ubuntu
brew install zbar           # macOS
```

**Tengo varias versiones de Python en Windows / Multiple Python versions on Windows**

Instala las dependencias especificando el Python exacto:
```bash
C:\Python311\python.exe -m pip install customtkinter pillow pyzbar opencv-python mss
```

Y ejecuta siempre con esa misma ruta:
```bash
C:\Python311\python.exe Google_auth_extractor.py
```

**Error al importar pyzbar en Windows**

`pyzbar` requiere librerías nativas. Si falla, `opencv-python` se usa automáticamente como alternativa — no necesitas hacer nada más.

---

## Seguridad / Security

- El código no hace ninguna conexión de red / No network connections
- Las claves TOTP nunca salen de tu equipo / TOTP secrets never leave your device
- Puedes auditar el código fuente completo aquí / Full source code available here

---

## Repositorio / Repository

[https://github.com/joseqwrtt/Google_auth_extractor](https://github.com/joseqwrtt/Google_auth_extractor)

---
<img width="649" height="724" alt="screenshot2" src="https://github.com/user-attachments/assets/e63a4706-ab28-47d3-afc5-46f7588e0abd" />

<img width="641" height="716" alt="screenshot3" src="https://github.com/user-attachments/assets/de41a90e-1467-419a-92b6-a1d0875ce1c9" />

<img width="658" height="727" alt="screenshot4_enEN" src="https://github.com/user-attachments/assets/fb567a63-b989-4eeb-9341-5e3c7e7cd18c" />

<img width="652" height="714" alt="screenshot4" src="https://github.com/user-attachments/assets/bb2bddfd-4c36-41a4-885a-894e54b40718" />

<img width="720" height="425" alt="screenshot1" src="https://github.com/user-attachments/assets/3bc9b0b4-905a-4cd7-8941-36421c4a6b75" />

---

## Licencia / License

MIT — úsalo, modifícalo y distribúyelo libremente. / Use it, modify it and distribute it freely.
