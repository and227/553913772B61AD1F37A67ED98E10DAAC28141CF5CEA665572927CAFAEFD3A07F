## Требования:
- docker-compose, 1.29.2
- python, 3.7+

## Пример настройки перед использованием:
```bash
docker exec -it charts-application python3 ./math_charts/manage.py makemigrations
docker exec -it charts-application python3 ./math_charts/manage.py migrate
docker exec -it charts-application python3 ./math_charts/manage.py createsuperuser --noinput --email useremail@gmail.com --username admin
```
