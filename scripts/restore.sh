#!/bin/bash
set -e

if [ -z "$1" ]; then
  echo "укажите путь к файлу бэкапа. Пример: ./scripts/restore.sh backups/backup_shortener_db_2026-11-17.sql.gz"
  exit 1
fi

if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

BACKUP_FILE=$1

echo "восстанавливаем базу ${POSTGRES_DB} из файла ${BACKUP_FILE}..."

gunzip -c "${BACKUP_FILE}" | docker exec -i shortener-db psql -U "${POSTGRES_USER}" -d "${POSTGRES_DB}"

echo "база данных успешно восстановлена!"
