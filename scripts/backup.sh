#!/usr/bin/env bash
# scripts/backup.sh - Utilidad de Snapshot pg_dump / pg_restore
set -euo pipefail

BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FILENAME="${BACKUP_DIR}/snapshot_${TIMESTAMP}.sql"

mkdir -p "$BACKUP_DIR"

case "${1:-backup}" in
  backup)
    echo "Generando snapshot de base de datos..."
    docker exec -i mapa_sabores_db pg_dump -U postgres -d mapa_sabores --clean --if-exists > "$FILENAME"
    echo "Snapshot guardado exitosamente en: $FILENAME"
    ;;
  restore)
    if [ -z "${2:-}" ]; then
      echo "Error: Debe especificar la ruta del archivo SQL a restaurar."
      echo "Uso: ./scripts/backup.sh restore ./backups/snapshot_YYYYMMDD_HHMMSS.sql"
      exit 1
    fi
    echo "Restaurando base de datos desde $2..."
    docker exec -i mapa_sabores_db psql -U postgres -d mapa_sabores < "$2"
    echo "Base de datos restaurada correctamente."
    ;;
  *)
    echo "Uso: ./scripts/backup.sh [backup|restore <archivo.sql>]"
    ;;
esac
