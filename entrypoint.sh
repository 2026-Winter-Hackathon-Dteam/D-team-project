#!/bin/sh
if [ ! "$(ls -A /code/staticfiles 2>/dev/null)" ]; then
echo "Collecting static files..."
python [manage.py](http://manage.py/) collectstatic --noinput
fi

exec "$@"