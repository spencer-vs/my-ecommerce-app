#t/usr/btn/env bash

set -o errexit # exit on error

pip install -r requirments.txt

python manage.py collectstatic --no-input
python manage.py migrate