web: bin/start-nginx bin/start-pgbouncer-stunnel newrelic-admin run-program gunicorn -c gunicorn.conf RealServer.wsgi:application
worker: bin/start-pgbouncer-stunnel celery -A RealServer worker -l info
beat: bin/start-pgbouncer-stunnel celery -A RealServer beat