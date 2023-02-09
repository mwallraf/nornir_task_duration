NAME=$(shell basename $(PWD))

PYTHON:=3.10.9

DOCKER_COMPOSE_FILE=docker-compose.yml
DOCKER_COMPOSE=docker-compose -f ${DOCKER_COMPOSE_FILE}

DOCKER=docker run \
	   --rm -it \
	   --name $(NAME)-tests \
	   -v $(PWD):/$(NAME) \
	   --rm $(NAME):latest

.PHONY: docker
docker:
	docker build \
	--build-arg PYTHON=$(PYTHON) \
	--build-arg NAME=$(NAME) \
	-t $(NAME):latest \
	-f Dockerfile \
	.

.PHONY: start_dev_env
start_dev_env:
	${DOCKER_COMPOSE} \
		up -d

.PHONY: stop_dev_env
stop_dev_env:
	${DOCKER_COMPOSE} \
		down
.PHONY: pytest
pytest:
	rm -f docs/source/tutorials/out_files/*.txt
	poetry run pytest --nbval -vs ${ARGS} docs/source/tutorials

.PHONY: black
black:
	poetry run black .

.PHONY: pylama
pylama:
	poetry run pylama .

.PHONY: isort
isort:
	poetry run isort nornir_task_duration

.PHONY: mypy
mypy:
	poetry run mypy nornir_task_duration

.PHONY: tests
tests: black isort pylama pytest


.PHONY: docker-tests
docker-tests: docker
	$(DOCKER) make tests

.PHONY: docs
docs:
	make -C docs html
