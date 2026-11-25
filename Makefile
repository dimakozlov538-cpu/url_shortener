.PHONY: up down restart logs ps backup

up:
	docker compose up -d --build

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

ps:
	docker compose ps

backup:
	./scripts/backup.sh
