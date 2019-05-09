# MongoDB ODS & Analytics on the DA Platform #

```
Copyright (c) 2019 Digital Asset (Switzerland) GmbH and/or its affiliates. All rights reserved.
SPDX-License-Identifier: Apache-2.0
```

## Overview ##

DAML is the perfect "gatekeeper" language for data persisted to a ledger, as it by designs both defines a strict data format and ensures that only conformant data ever gets persisted - in the form of a contract. 

This removes a large part of the ETL burden, and allows data coming off a ledger to be input straight into MongoDB, with all MongoDB's native tools immediately available.

The aim of this demo is to investigate how easily MongoDB can be purposed as a data store for records coming off the ledger, and how easily insights can be gained from the data. 

## The data ##

The movie ratings data set is ideal to use to explore MongoDB's aggregation operations as it contains multiple entries for a given movie, which allows for both exploratory investigation using Compass, and also drilling down using the command line client, to harness the power of pipelines. 

## Dependencies ##

| Required |
|---|
| GNU Make |
| Docker (Community Edition) |
| `docker-compose` _(From GitHub, not `apt`)_ |
| Python Pipenv _(via `pip install`)_ |
| DAZL _(Tested for version `5.5.2`)_ |
| MongoDB Compass (Stable) |

## Setup and Data loading ##

The project is managed by a `Makefile`. Initially one needs to pull in the required data sources, docker images and dependencies, via:

```sh
$ make setup
```

To spin everything up and start the MongoDB and RabbitMQ containers, opens ports, compiles DARs, spin up the data submitter pipeline and spin up a Navigator instance on `TCP/4000`, run:

```sh
$ make start
```

To setup a nanobot to read off the ledger and populate MongoDB, in a new terminal, run:

```sh
$ pipenv run python ./app/operator_listener.py --config config.yaml --user Data_Scientist
```

And finally, to start the data loader, in a new terminal, run:

```sh
$ pipenv run python generators/operator_loader.py --config config.yaml --user Data_Scientist --test NUM
```

where `NUM` specifies the number of ratings to submit. This will also create the initial _analyst_ user, under whom all rater and rating information is loaded onto the ledger.

If `--test NUM` is not specified, then the entire ratings matrix is loaded, wich is 100,836 entries. Please see **Performance Considerations** below.

## Monitoring ##

Navigator can be used to inspect the ledger and the contracts being created. Go to <http://localhost:4000> and login as user **Data_Scientist** (the only option in the dropdown).

## MongoDB Analytics ##

This is where the fun begins! See - [MongoDB Aggregation Operations](docs/MongoDB_Aggregation_Operations.pdf) for more details.

## Teardown ##

```sh
$ make stop
```

will shutdown the submitter, kill the sandbox and stop the containers and to stop Navigator.

To do a clean up on the runtime logs, run:

```sh
$ make clean
```

To do a final clean up on the data source directory as well, run:

```sh
$ make data-clean
```

## Performance considersations ##

This is a lengthy and very resource-intensive process that can create 100K+ ratings (and corresponding users as necessary), and it takes approximately 15 minutes to orchestrate the setup, and a LOT longer for the load to complete - in the order of hours. This is, naturally, dependent on how beefy your system setup is and the number of cores and RAM available to you.

It's difficult to determine the granularity of the time breakdown, but when last tested it was the gRPC libraries which appeared to be the problem - or some combination software and hardware. Furthermore, the thread multiplier settings in `config.yaml` are fairly aggressive and pretty much run all cores at 100%, de-tuning that somewhat could alleviate performance lag and lock-ups.

## Links ##

- DAML: <https://daml.com>
- `docker`: <https://docs.docker.com/install/linux/docker-ce/ubuntu/>
- `docker-compose`: <https://docs.docker.com/compose/install/>
- MongoDB Compass: <https://www.mongodb.com/download-center/compass?jmp=hero>
- Random user generation: <https://randomuser.me/documentation>
- Movie ratings data set: <https://grouplens.org/datasets/movielens/>
- MongoDB Manual - Aggregation <https://docs.mongodb.com/manual/aggregation>
