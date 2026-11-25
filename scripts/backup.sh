#!/bin/bash
set -e

if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILE="${BACKUP_DIR}/backup_${POSTGRES_DB}_${TIMESTAMP}.sql.gz"

echo "начинаем резервное копирование базы ${POSTGRES_DB}..."

# Делаем дамп внутри контейнера Postgres и сразу сжимаем на хосте
docker exec -t shortener-db pg_dump -U "${POSTGRES_USER}" "${POSTGRES_DB}" | gzip > "${BACKUP_FILE}"

echo "бэкап успешно создан: ${BACKUP_FILE}"

# Удаляем архивы старше 7 дней (ротация бэкапов)
find "${BACKUP_DIR}" -type f -name "*.sql.gz" -mtime +7 -delete
echo "старые бэкапы (старше 7 дней) delete."
