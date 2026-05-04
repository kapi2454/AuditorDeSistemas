# 📊 Auditor de Sistemas Inteligente (Gemini AI)

Este proyecto es un bot de auditoría automatizada que analiza la salud de servidores Linux (Ubuntu/Debian) y reporta el estado de versiones de software (PHP, MariaDB, OS) y alertas de seguridad SSH mediante la IA de Google Gemini.

## 🚀 Características
- **Auditoría de Software:** Detecta versiones instaladas y evalúa su ciclo de vida (EOL).
- **Seguridad en Tiempo Real:** Analiza `/var/log/auth.log` en busca de ataques de fuerza bruta.
- **Reportes automáticos:** Envía un resumen formateado a Telegram.
- **Alertas Críticas:** Clasifica problemas en ✅ OK, ⚠️ Advertencia y 🔴 Crítico.

## 🛠️ Instalación en Ubuntu 22.04+

### 1. Clonar y Preparar el Entorno
```bash
cd ~/scripts
git clone [https://github.com/tu-usuario/AuditorDeSistemas.git](https://github.com/tu-usuario/AuditorDeSistemas.git) .
pip install -r requirements.txt
```

##🤖 Configuración de Telegram (Bot Father)

Para que el script pueda enviarte mensajes, necesitas crear un bot y obtener tu ID de usuario:

    Crear el Bot:
        Busca a @BotFather en Telegram.
        Escribe /newbot y sigue las instrucciones para darle un nombre.
        Al finalizar, te dará el TELEGRAM_TOKEN (guárdalo, es tu llave).
    Obtener tu Chat ID:
        Para saber a qué chat debe escribir el bot, busca el bot @userinfobot en Telegram y envíale cualquier mensaje.
        Te responderá con un número (ej: 123456789). Ese es tu TELEGRAM_CHAT_ID.
    Activar el Bot:
        Busca tu nuevo bot por el nombre que le pusiste y dale a /start. Si no le escribes primero, el bot no tendrá permiso para enviarte mensajes.


## 2. Configurar Variables de Entorno

Crea un archivo .env en la raíz del proyecto (este archivo está protegido por .gitignore):
Ini, TOML

```bash
GEMINI_API_KEY=tu_nueva_api_key_aqui
TELEGRAM_TOKEN=tu_token_de_bot
TELEGRAM_CHAT_ID=tu_id_de_chat
```

## 3. Configurar Permisos de Seguridad

Para que el script pueda leer los logs de SSH sin necesidad de usar sudo, añade tu usuario al grupo adm:

```bash
sudo usermod -aG adm $USER
```

# IMPORTANTE: Cierra y abre sesión para que los cambios surtan efecto.

4. Protección Perimetral (Recomendado)

Para mitigar los ataques que el bot detecte, instala y configura Fail2Ban:

```bash
sudo apt install fail2ban -y
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
# Editar /etc/fail2ban/jail.local para habilitar [sshd] con enabled = true
sudo systemctl restart fail2ban
```

## 📅 Automatización (Cron)

Para recibir un reporte diario a las 08:05 AM, añade la siguiente línea a tu crontab -e:
Fragmento de código

```bash
5 8 * * * /usr/bin/python3 ~/scripts/auditor_inteligente.py >> ~/scripts/log_auditoria.txt 2>&1
```

⚠️ Notas de Seguridad

    No subir el archivo .env: Contiene claves privadas.

    No hardcodear claves: Siempre usar os.getenv() para llamar a las API Keys.

    Acceso Root: Se recomienda deshabilitar PermitRootLogin en /etc/ssh/sshd_config una vez verificado el funcionamiento.
