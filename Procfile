web: gunicorn RealServer.wsgi --log-file -w 1
worker: celery -A RealServer worker -l info -c 1