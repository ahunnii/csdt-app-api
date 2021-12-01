docker compose run --rm app sh -c "python manage.py makemigrations core"
docker compose run --rm app sh -c "python manage.py migrate"
