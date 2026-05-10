#!/bin/bash
# =================================================================
# AWS SSO REFRESHER & STEERING SYNC (Debian WSL)
# Autenticación: AWS SSO + Azure DevOps PAT (extraído de mcp.json)
#
# Este script se auto-actualiza desde el repo en cada ejecución.
# Para modificarlo, editá scripts/aws-refresh.sh en el repo Git.
# =================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'  # reset

set -e

SSO_PROFILE="KiroProUsers-905418430766"
REGION="us-east-1"
SSO_START_URL="https://d-9067fed560.awsapps.com/start"
STEERING_REPO="$HOME/kiro-steering"
MCP_CONFIG="$HOME/.kiro/settings/mcp.json"

echo "===================================================="
echo "    AWS SSO REFRESHER & KIRO STEERING SYNC"
echo "    Usuario: $USER"
echo "===================================================="

# 1. Extraer PAT de Azure DevOps desde mcp.json
echo "1. Validando credenciales de Azure DevOps..."
if [ ! -f "$MCP_CONFIG" ]; then
    echo "    [ERROR] No se encontró $MCP_CONFIG."
    echo "    Ejecutá el instalador: bash ~/kiro-steering/install.sh"
    exit 1
fi

ADO_KIRO_PAT=$(python3 -c \
    "import sys,json; print(json.load(open(sys.argv[1]))['mcpServers']['azure-devops']['env']['AZURE_DEVOPS_EXT_PAT'])" \
    "$MCP_CONFIG")

if [ -z "$ADO_KIRO_PAT" ] || [ "$ADO_KIRO_PAT" = "CONFIGURAR_PAT" ]; then
    echo "    [ERROR] El PAT no está configurado en $MCP_CONFIG."
    echo "    Editalo con: nano $MCP_CONFIG"
    exit 1
fi

CLEAN_PAT=$(echo "$ADO_KIRO_PAT" | tr -d '\r\n ')
echo "    PAT detectado correctamente."

export GIT_TERMINAL_PROMPT=0
export GCM_INTERACTIVE=never

# 2. Login AWS SSO
echo "2. Iniciando Login AWS SSO..."
aws sso login --profile $SSO_PROFILE

# 3. Exportar credenciales al perfil default
echo "3. Actualizando perfiles de AWS..."
CREDS=$(aws configure export-credentials --profile $SSO_PROFILE --output json)

if [ -z "$CREDS" ]; then
    echo "    [ERROR] No se pudieron obtener credenciales de AWS."
    exit 1
fi

ACCESS_KEY=$(echo $CREDS    | python3 -c "import sys,json; print(json.load(sys.stdin)['AccessKeyId'])")
SECRET_KEY=$(echo $CREDS    | python3 -c "import sys,json; print(json.load(sys.stdin)['SecretAccessKey'])")
SESSION_TOKEN=$(echo $CREDS | python3 -c "import sys,json; print(json.load(sys.stdin)['SessionToken'])")
EXPIRATION=$(echo $CREDS    | python3 -c "import sys,json; print(json.load(sys.stdin)['Expiration'])")

aws configure set aws_access_key_id     "$ACCESS_KEY"
aws configure set aws_secret_access_key "$SECRET_KEY"
aws configure set aws_session_token     "$SESSION_TOKEN"
aws configure set region                "$REGION"

# 4. Asumir KiroReaderRole y setear perfil kiro-handy-global
echo "4. Asumiendo KiroReaderRole..."
READER_CREDS=$(aws sts assume-role \
    --role-arn arn:aws:iam::905418430766:role/KiroReaderRole \
    --role-session-name "KiroSession-$USER" \
    --profile "$SSO_PROFILE" \
    --output json)

R_ACCESS=$(echo $READER_CREDS | python3 -c "import sys,json; print(json.load(sys.stdin)['Credentials']['AccessKeyId'])")
R_SECRET=$(echo $READER_CREDS | python3 -c "import sys,json; print(json.load(sys.stdin)['Credentials']['SecretAccessKey'])")
R_TOKEN=$(echo $READER_CREDS  | python3 -c "import sys,json; print(json.load(sys.stdin)['Credentials']['SessionToken'])")

aws configure set aws_access_key_id     "$R_ACCESS" --profile kiro-handy-global
aws configure set aws_secret_access_key "$R_SECRET" --profile kiro-handy-global
aws configure set aws_session_token     "$R_TOKEN"  --profile kiro-handy-global
aws configure set region                "$REGION"   --profile kiro-handy-global

# 5. Sincronizar repo (steering files + versión del script)
echo "5. Sincronizando repositorio kiro-steering..."
AUTHED_URL="https://${CLEAN_PAT}:${CLEAN_PAT}@dev.azure.com/handy-uy/Infraestructura/_git/kiro-steering"

if [ -d "$STEERING_REPO/.git" ]; then
    cd "$STEERING_REPO"
    git remote set-url origin "$AUTHED_URL"
    git -c http.version=HTTP/1.1 pull --quiet
else
    echo "    [WARN] Repo no encontrado, clonando de nuevo..."
    git -c http.version=HTTP/1.1 clone --quiet "$AUTHED_URL" "$STEERING_REPO"
fi
find "$STEERING_REPO" -name "*.sh" -exec dos2unix {} \; 2>/dev/null || true

# 6. Auto-actualizar este script desde el repo
echo "6. Verificando versión del script..."
SCRIPT_IN_REPO="$STEERING_REPO/scripts/aws-refresh.sh"
SCRIPT_LOCAL="$HOME/aws-refresh.sh"

if [ -f "$SCRIPT_IN_REPO" ]; then
    dos2unix "$SCRIPT_IN_REPO" 2>/dev/null || true
    if ! diff -q "$SCRIPT_IN_REPO" "$SCRIPT_LOCAL" > /dev/null 2>&1; then
        cp "$SCRIPT_IN_REPO" "$SCRIPT_LOCAL"
        chmod +x "$SCRIPT_LOCAL"
        echo "    Script actualizado desde el repo."
    else
        echo "    Script ya en la versión más reciente."
    fi
else
    echo "    [WARN] No se encontró $SCRIPT_IN_REPO — saltando auto-update."
fi

# 7. Verificar symlinks de steering
echo "7. Verificando steering files..."
mkdir -p ~/.kiro/steering/
ln -sf "$STEERING_REPO/shared/steering-tech.md"        ~/.kiro/steering/tech.md
ln -sf "$STEERING_REPO/shared/steering-preferences.md" ~/.kiro/steering/preferences.md
ln -sf "$STEERING_REPO/shared/steering-security.md"    ~/.kiro/steering/security.md

# 8. Renovar login de Kiro
echo "8. Renovando login de Kiro..."
export PATH="$HOME/.local/bin:$PATH"
if kiro-cli whoami &>/dev/null; then
    echo "    Ya autenticado en Kiro."
else
    kiro-cli login --license pro \
        --identity-provider "$SSO_START_URL" \
        --region "$REGION"
fi

echo ""
echo "¡ÉXITO! Todo configurado."
echo "Tokens de AWS expiran: $EXPIRATION"
echo ""
source ~/.bashrc 2>/dev/null || true
export PATH="$HOME/.local/bin:$PATH"
echo -e "Ya podés usar:  ${RED}kiro-cli chat ${NC}"
echo -e "${YELLOW}Si kiro-cli no se encuentra ejecutá: ${RED} source ~/.bashrc${NC}"
