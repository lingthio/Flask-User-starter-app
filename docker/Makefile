NAME=issm
VERSION=$(shell cat ../Version)
PYTHON=python
DOCKER=docker

.PHONY: build clean run daemon stop it

build:
	cd .. && $(DOCKER) build -t $(NAME):$(VERSION) .

run:
	$(DOCKER) run --rm -d \
		-p 8080:80 -p 5000:5000 \
		-e DEBUG=1 \
		--name $(NAME) \
		$(NAME):$(VERSION)

debug:
	$(DOCKER) run --rm -it \
		-p 8080:80 -p 5000:5000 \
		-e DEBUG=1 \
		-e ADMINS="admin@issm.org" \
		--name $(NAME) \
		--entrypoint="" \
		-w "/issm" \
		$(NAME):$(VERSION) \
		/bin/bash -c "\
			./manage.py init_db && \
			./manage.py runserver --host=0.0.0.0"

daemon:
	$(DOCKER) run -d \
		--name $(NAME) \
		--restart unless-stopped \
		$(NAME):$(VERSION)

stop:
	$(DOCKER) rm --force $(NAME)

clean:
	$(DOCKER) rmi --force $(NAME):$(VERSION)

it:
	$(DOCKER) exec -it $(NAME) /bin/bash
