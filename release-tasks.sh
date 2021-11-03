#!/bin/sh
cd purbeurre/ || exit
python manage.py migrate
python manage.py populate
python manage.py algolia_reindex
