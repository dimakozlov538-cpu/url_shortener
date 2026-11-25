# URL Shortener Service (Production-Ready DevOps Infrastructure)

![Repository](https://img.shields.io/badge/Repository-GitHub-181717?logo=github&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?logo=nginx&logoColor=white)
![Monitoring](https://img.shields.io/badge/Monitoring-Prometheus_%2B_Grafana-E6522C?logo=prometheus&logoColor=white)

Высокодоступный сервис сокращения ссылок с полноценной production-инфраструктурой: контейнеризацией, обратным проксированием, мониторингом метрик и автоматическим резервным копированием данных.

## Архитектура проекта

Вся инфраструктура оркестрируется через **Docker Compose** и разделена на изолированные сервисы для приема трафика, обработки бизнес-логики, хранения данных и сбора метрик:

```mermaid
flowchart LR
    Client([Пользователь]) --> Nginx[Nginx<br/>Reverse Proxy]
    Nginx --> App[Backend App<br/>Python API]
    App --> DB[(База данных /<br/>Кэш)]
    Monitoring[Monitoring<br/>Prometheus / Grafana] -.-> Nginx
    Monitoring -.-> App
    Scripts[Scripts<br/>Backup Cron] --> Backups[(Backups<br/>Дампы БД)]
```

## Реализованные DevOps практики

- **Контейнеризация и оркестрация (`Dockerfile` & `docker-compose.yml`):**
  - Многосервисная сборка с изоляцией контейнеров во внутренней Docker-сети.
  - Конфигурация приложения вынесена в переменные окружения (`.env`), а лишние файлы исключены из контекста сборки через `.dockerignore`.
  - Настроены политики перезапуска контейнеров (`restart: unless-stopped`) и проверки состояния (`HEALTHCHECK`).

- **Reverse Proxy и балансировка (`nginx/`):**
  - **Nginx** выступает единой точкой входа, проксируя запросы к backend-приложению.
  - Настроено сжатие трафика (`gzip`), таймауты соединений и базовые заголовки безопасности.

- **Мониторинг и наблюдаемость (`monitoring/`):**
  - Выделенный стек мониторинга для отслеживания доступности сервиса, времени отклика (latency), кодов ответов HTTP и утилизации ресурсов контейнеров.

- **Резервное копирование и автоматизация (`scripts/` & `backups/`):**
  - Скрипты автоматического создания и ротации бэкапов данных с сохранением дампов в директорию `backups/`.

## Локальный запуск (через Makefile)

Для удобного управления стеком локально и на сервере используется `Makefile` *(проверьте названия таргетов в вашем `Makefile`)*:

```bash
# Собрать образы и запустить все сервисы в фоновом режиме
make up

# Посмотреть статус контейнеров и их состояние
make status

# Посмотреть логи сервисов в реальном времени
make logs

# Создать резервную копию базы данных вручную
make backup

# Пересобрать контейнеры после внесения изменений в код
make restart

# Остановить сервисы и очистить ресурсы
make down
```

## Структура проекта

```text
.
├── app/                   # Исходный код сервиса сокращения ссылок
├── backups/               # Директория для хранения резервных копий
├── monitoring/            # Конфигурация мониторинга и дашбордов
├── nginx/                 # Конфигурационные файлы Nginx (reverse proxy)
├── scripts/               # Скрипты автоматизации и резервного копирования
├── .dockerignore          # Исключения для сборки Docker-образа
├── .env                   # Переменные окружения (рекомендуется заменить на .env.example)
├── .gitignore             # Исключения для Git
├── Dockerfile             # Сборка образа приложения
├── Makefile               # Автоматизация управления проектом
├── docker-compose.yml     # Описание и оркестрация всех сервисов
├── requirements.txt       # Python-зависимости приложения
└── README.md              # Документация проекта
```
