python3 /opt/issuebox/issuebox/manage.py loaddata default_tags.json
python3 /opt/issuebox/issuebox/manage.py migrate
python3 /opt/issuebox/issuebox/manage.py runserver 0.0.0.0:8003
