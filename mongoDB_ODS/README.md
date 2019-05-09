```
Copyright (c) 2019 Digital Asset (Switzerland) GmbH and/or its affiliates. All rights reserved.
SPDX-License-Identifier: Apache-2.0
```

# MongoDB ODS & Analytics on the DA Ledger

## Overview



## Workflow

### Elements

1. Payload generation process ("_datagen nanobot_")
1. (Rabbit)MQ Pub/Sub queue for the listener nanobot to 
1. Subscriber service ("_listener nanobot_") to consume an event stream from the ledger and create documents within MongoDB

## The demo

### Setup the Environment

1. Pull in the required data sources, docker images and dependencies by running:
    ```sh
    $ make setup
    ```

### Running the Demo

1. Spin everything up and start the MongoDB and RabbitMQ containers, open ports, compile DARs, spin up the data submitter pipeline and spin up a Navigator instance on `TCP/4000`. To do this, run:

    ```sh
    $ make start
    ```

1. Set up the subscriber service listener nanobot to read off the ledger and populate MongoDB - open a new terminal and run:

    ```sh
    $ pipenv run python ./app/operator_listener.py --config config.yaml --user Data_Scientist
    ```

1. Open a new terminal and start the datagen nanobot loader by running:
    ```sh
    $ pipenv run python generators/operator_loader.py --config config.yaml --user Data_Scientist --test NUM
    ```

    where `NUM` specifies the number of ratings to submit. This will also create the initial _Data_Scientist_ user, under whom all rater and rating information is loaded onto the ledger.

    If you don't include `--test NUM`, the entire ratings matrix is loaded: 100,836 entries. Please see **Performance Considerations** below.

1. To shut down the submitter, the sandbox, the containers, and Navigator, run:

    ```sh
    $ make stop
    ```

1. To do a clean up on the runtime logs, run:

    ```sh
    $ make clean
    ```

1. To do a final clean up on the data source directory as well, run:

    ```sh
    $ make data-clean
    ```

### Performance Considerations

The data loader is resource-intensive, and works in two phases:

1. Queue Setup - for each rating in the set:
    1. An user record is generated (if the user doesn't already exist) and pushed onto the MQ
    1. A movie rating record is generated and pushed onto the MQ 
1. Data Submission
    1. Records are popped from the MQ, commands are generated and submitted

Predictably, the total runtime depends on the value of `NUM`; for example - submitting 100K+ ratings (and corresponding users) takes around fifteen minutes to setup the queue, but a LOT longer (in the order of hours) for the submission to complete. 

The runtime, naturally, is dependent on how beefy your system setup is and the number of cores and RAM available to you. It's difficult to determine the exact time breakdown, but different combinations of software and settings do make an impact. The thread multiplier settings in `config.yaml` are fairly aggressive and pretty much run all cores at 100%, de-tuning that could alleviate some performance lag and lock-ups.

## MongoDB Aggregation Pipeline Operations


## Extending the Demo

One of the aims of this demo was to investigate the feasibility 

![GitHub Logo](/images/logo.png)
<!-- (/images/MongoDB_demo_arch-Virtuous circle.png) -->

## Links ##

- DAML: <https://daml.com>
- `docker`: <https://docs.docker.com/install/linux/docker-ce/ubuntu/>
- `docker-compose`: <https://docs.docker.com/compose/install/>
- MongoDB Compass: <https://www.mongodb.com/download-center/compass?jmp=hero>
- Random user generation: <https://randomuser.me/documentation>
- Movie ratings data set: <https://grouplens.org/datasets/movielens/>
- MongoDB Manual - Aggregation <https://docs.mongodb.com/manual/aggregation>
