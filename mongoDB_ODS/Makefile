# Copyright 2019 Digital Asset (Switzerland) GmbH and/or its affiliates.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

project_name	:=	"MongoDB_ODS"
docker_file	:=	"docker-compose.yaml"
source_file	:=	"ml-latest-small.zip"
logs_dir	:=	"logs"
sandbox_ip	:=	127.0.0.1
sandbox_port	:=	3999
navigator_port	:=	4000

all:
	@echo "'setup' - fetch and extract data sources"
	@echo "'start' - starts all services"
	@echo "'stop' - stops all services"
	@echo "'clean' - remove runtime logs"
	@echo "'data-clean' - remove data sources"
	@echo "'db-cli' - run mongodb client in a container"

setup:
	mkdir -p $(logs_dir)
	docker pull mongo:latest
	docker pull rabbitmq:latest
	mkdir -p data
	wget -rc "http://files.grouplens.org/datasets/movielens/$(source_file)" -O /tmp/$(source_file)
	unzip -o /tmp/$(source_file) -d ./data
	pipenv lock --pre
	pipenv run pip install pip==19.0
	pipenv install --pre
	pipenv sync --pre

start:
	@echo 'users { Data_Scientist { party = "Data_Scientist", }, }' > .navigator.conf && echo "Generated Navigator config"
	docker-compose -f $(docker_file) -p $(project_name) up -d 
	da compile
	da run sandbox -- --port $(sandbox_port) --address $(sandbox_ip) --wall-clock-time target/$(project_name).dar 2>&1 > $(logs_dir)/sandbox-manual.log &
	pipenv run celery --app=generators.submitter worker --pidfile /tmp/submitter.pid --logfile $(logs_dir)/submitter.log --loglevel info --detach --concurrency $(shell echo "`cat /proc/cpuinfo | grep \^processor | wc -l`*2" | bc)
	da run navigator 2> $(logs_dir)/navigator.log -- server --port $(navigator_port) -c `pwd`/.navigator.conf -t wallclock $(sandbox_ip) $(sandbox_port) &

stop:
	kill -INT $(shell ps -x | grep "[n]avigator-" | grep $(navigator_port) | awk '{print $$1}') || echo "Navigator not running"
	pipenv run celery --app=generators.submitter control shutdown || echo "Success"
	kill -INT $(shell ps -x | grep "[s]andbox-" | grep $(sandbox_port) | awk '{print $$1}') || echo "Sandbox not running"
	docker-compose -f $(docker_file) -p $(project_name) down 

clean:
	rm -rfv sandbox.log navigator.log logs/*

data-clean:	clean
	rm -rfv data/

db-cli:
	docker run -i -t --rm mongo:latest sh -c "mongo $(shell ifconfig docker0 | grep -w inet | awk '{print $$2}')"
