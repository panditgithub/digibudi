# digibuddies

Install redis server

Create Enviroment

pip install -r requirements.txt

Make migration
<ul>
<li>python manage.py makemigrations</li>
<li>python manage.py makemigrations mainapp</li>
<li>python manage.py makemigrations chat</li>
</ul>
Migrate:
python mannage.py migrate

run server:
python manage.py runserver

run celery beat:
celery -A digibuddies.celery  worker --loglevel=info;
