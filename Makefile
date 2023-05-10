dev:
	pip install -r requirements.txt

makemigrations:
	python ./social_network_backend/manage.py makemigrations

migrate:
	python ./social_network_backend/manage.py migrate

runserver:
	python ./social_network_backend/manage.py runserver

run:
	make makemigrations
	make migrate
	make runserver