#!/bin/bash
# Navegar a la carpeta del script
cd ~/scripts

# Bajar los cambios de GitHub
git pull origin main

# Asegurarse de que las librerías necesarias estén instaladas
pip install -r requirements.txt --quiet

# Dar permisos de ejecución por si acaso
chmod +x ~/scripts/auditor_inteligente.py
