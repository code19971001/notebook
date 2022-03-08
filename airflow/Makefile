PACKAGES := "dags"


.PHONY: build
build:
	docker build . -f Dockerfile --tag airflow:code1997

.PHONY: version
version:
	docker run --rm --name testairflow airflow:code1997 version

.PHONY: up
up:
	docker-compose up

.PHONY: down
down: 
	docker-compose down