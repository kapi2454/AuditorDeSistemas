# 🔍 Auditor Inteligente de Sistemas

Script de auditoría de seguridad para servidores Linux. Analiza versiones de software, intentos de acceso SSH fallidos y envía un reporte diario por Telegram usando **Gemini AI**.

Diseñado para funcionar en múltiples instancias con un único repositorio compartido.

---

## ✨ Características

- 📊 Reporte diario de versiones de SO, PHP y MariaDB con estado de soporte
- 🔒 Análisis de intentos SSH fallidos con detección de fuerza bruta
- 🤖 Análisis inteligente con Gemini AI (modelo `gemini-flash-latest`)
- 📱 Envío automático por Telegram
- 🌍 Compatible con Ubuntu 22.04 y 24.04+ (detección automática de fuente de logs)
- 🏷️ Nombre de servidor configurable por instancia vía `.env`
- 📅 Fecha dinámica — siempre reporta el mes y año actuales

---

## 📋 Requisitos

- Python 3.10+
- API Key de [Google AI Studio](https://aistudio.google.com) (Gemini)
- Bot de Telegram con token y chat ID

---

## 🚀 Instalación

```bash
git clone https://github.com/kapi2454/AuditorDeSistemas scripts
cd scripts
pip install -r requirements.txt --quiet
# Ubuntu 24.04+:
# pip install -r requirements.txt --quiet --break-system-packages
```

---

## ⚙️ Configuración

Creá el archivo `.env` en la carpeta del script:

```env
GEMINI_API_KEY=tu_api_key_aqui
TELEGRAM_TOKEN=tu_bot_token_aqui
TELEGRAM_CHAT_ID=tu_chat_id_aqui
SERVER_NAME=NombreDelServidor
```

> **`SERVER_NAME`** es opcional. Si no está definido, usa el hostname del sistema automáticamente.

---

## 📦 Dependencias

```
google-genai==1.74.0
python-dotenv==1.2.2
requests==2.33.1
requests-toolbelt==0.9.1
```

---

## ▶️ Uso

Ejecutar manualmente:
```bash
python3 auditor_inteligente.py
```

---

## ⏰ Automatización con cron

El repositorio incluye `actualizar_auditor.sh` que hace `git pull` y actualiza dependencias antes de cada ejecución.

Configuración recomendada en `crontab -e`:

```
# Actualizar código desde GitHub a las 8:00 AM
0 8 * * * /bin/bash ~/scripts/actualizar_auditor.sh >> ~/scripts/log_git.txt 2>&1

# Ejecutar auditoría 5 minutos después
5 8 * * * /usr/bin/python3 ~/scripts/auditor_inteligente.py >> ~/scripts/log_auditoria.txt 2>&1
```

---

## 📱 Ejemplo de reporte

```
📊 *Resumen MiServidor*

Componente | Est | Versión
-----------|-----|--------
SO         | OK  | Ubuntu 24.04.4 LTS
PHP        | ⚠️  | 8.3.6
MariaDB    | OK  | 10.11.14

⚠️ PHP 8.3: Se aproxima al fin de soporte de seguridad (finales 2026).
⚠️ MariaDB 10.11: Requiere verificar parches de seguridad recientes.
```

Con ataques detectados:
```
📊 *Resumen MiServidor*

Componente | Est | Versión
...

🔒 SEGURIDAD SSH
3 intentos fallidos desde IPs externas en las últimas 24h.

⚠️ ...
```

---

## 🖥️ Compatibilidad de logs SSH

| OS | Fuente de logs |
|---|---|
| Ubuntu 22.04 | `/var/log/auth.log` |
| Ubuntu 24.04+ | `journalctl _SYSTEMD_UNIT=ssh.service` |

El script detecta automáticamente cuál usar.

---

## 🏗️ Estructura del repositorio

```
scripts/
├── auditor_inteligente.py   # Script principal
├── actualizar_auditor.sh    # Script de actualización desde GitHub
├── requirements.txt         # Dependencias Python
├── .env                     # Credenciales (NO commitear)
└── README.md
```

> ⚠️ **El archivo `.env` nunca debe subirse al repositorio.** Asegurate de que está en `.gitignore`.

---

## 🔐 Seguridad

- Rotá las API keys periódicamente
- El `.env` debe tener permisos restrictivos: `chmod 600 .env`
- Nunca commitees credenciales al repositorio

---

## 📍 Instancias activas

| Servidor | IP | OS | Nombre |
|---|---|---|---|
| Alamos | `170.187.136.237` | Ubuntu 22.04 LTS | Alamos |
| MiTecnico | `155.248.219.40` | Ubuntu 24.04 LTS | MiTecnico |
