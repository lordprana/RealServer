#web: gunicorn RealServer.wsgi --log-file -
#worker: celery -A RealServer worker -l info
web: bin/start-nginx bin/start-pgbouncer-stunnel gunicorn -c gunicorn.conf RealServer.wsgi:application
worker: bin/start-pgbouncer-stunnel celery -A RealServer worker -l info