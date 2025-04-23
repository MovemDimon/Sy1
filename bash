docker-compose up --build
docker-compose exec app flask db init
docker-compose exec app flask db migrate
docker-compose exec app flask db upgrade
docker-compose exec celery celery -A app.services.celery_worker worker --loglevel=info
