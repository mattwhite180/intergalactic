#!/bin/bash
# hostname -I
# hostname -I
# hostname -I
# hostname -I
# hostname -I
# hostname -I
# hostname -I
# echo 'sleeping for 5'
# sleep 5
# echo 'done sleeping. running migrations'
# python3 manage.py makemigrations gameapp && \
# python3 manage.py makemigrations
# python3 manage.py makemigrations && \
# python3 manage.py migrate && \
# echo 'done with migrations. running server'
python3 manage.py collectstatic
python3 manage.py runserver 0:8000
