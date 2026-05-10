import os
import socket
import subprocess
import requests
from google import genai
from dotenv import load_dotenv
from datetime import datetime

# Cargamos las variables del archivo .env
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SERVER_NAME = os.getenv("SERVER_NAME", socket.gethostname())

client = genai.Client(api_key=GEMINI_API_KEY)

def get_system_info():
    os_v = subprocess.getoutput("lsb_release -ds 2>/dev/null || ...")
    php_v = subprocess.getoutput("php -v | head -n 1")
    db_v = subprocess.getoutput("mariadb --version 2>/dev/null || mysql --version 2>/dev/null || echo 'No detectada'")
    nc_v = subprocess.getoutput("cat /var/www/html/version.php 2>/dev/null | grep OC_VersionString | cut -d\\' -f2 || echo 'No instalado'")
    return f"SO: {os_v} | PHP: {php_v} | DB: {db_v} | Nextcloud: {nc_v}"

def enviar_telegram(texto):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    # Usamos Markdown normal
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": texto, "parse_mode": "Markdown"}
    requests.post(url, json=payload)
    
def get_ssh_attempts():
    log_path = "/var/log/auth.log"
    if os.path.exists(log_path):
        ssh_log = subprocess.getoutput(f"grep 'Failed password' {log_path} | tail -n 5")
    else:
        ssh_log = subprocess.getoutput(
            "journalctl _SYSTEMD_UNIT=ssh.service --since '24 hours ago' | grep 'Failed password' | tail -n 5"
        )
    if not ssh_log.strip():
        ssh_log = "Sin intentos fallidos recientes."
    return ssh_log

def ejecutar_auditoria():
    info = get_system_info()
    ssh_info = get_ssh_attempts()
    prompt = f"""
    Analiza la seguridad del servidor {SERVER_NAME} a fecha {datetime.now().strftime("%B %Y")}.
    NOMBRE DEL SERVIDOR: {SERVER_NAME}
    
    DATOS DEL SISTEMA:
    1. Versiones: {info}
    2. Intentos SSH fallidos: {ssh_info}
    
    Genera el reporte EXACTAMENTE así:
    1. Frase inicial: 📊 *Resumen {SERVER_NAME}*
    2. Tabla de versiones en bloque de código (
```) como ya sabes hacer (Componente | Est | Versión).
    3. Si detectas ataques de fuerza bruta en los logs SSH (muchos intentos de IPs externas), 
       añade una sección abajo llamada "🔒 SEGURIDAD SSH" con un resumen muy corto.
    4. Lista corta de riesgos (⚠️ o 🔴) de las versiones de software.
    
    Sé extremadamente breve y directo.
    """
        
    try:
        response = client.models.generate_content(
            model="gemini-flash-latest", 
            contents=prompt
        )
        
        # El reporte ya vendrá con el formato correcto desde Gemini
        reporte = response.text
        print(reporte)
        enviar_telegram(reporte)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    ejecutar_auditoria()
