web: uwsgi --http-socket=0.0.0.0:$PORT --virtualenv=$PYTHONHOME --master --processes=1 --pythonpath=$HOME --module="spa.wsgi:application" --static-map /static=$HOME/spa/static_root
