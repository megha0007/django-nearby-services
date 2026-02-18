## Docker Commands

Start application:
    docker compose up --build

Stop application (keep database):
    docker compose down

Reset database (remove volumes):
    docker compose down -v

Database persistence is handled via a named Docker volume.
