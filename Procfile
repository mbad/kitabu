web: example_project/manage.py syncdb --migrate --noinput --settings='spa.settings_heroku' && uwsgi --http-socket=0.0.0.0:$PORT --virtualenv=$PYTHONHOME --master --processes=1 --pythonpath=$HOME/example_project --module="spa.wsgi:application"