# Copyright (c) 2019 Digital Asset (Switzerland) GmbH and/or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from celery import Celery
from dazl import Network, simple_client, create


mq = Celery(broker = 'pyamqp://guest@localhost//')


@mq.task
def add_rater(submitter, endpoint, person, personInfo):
  network = Network()
  network.set_config(url = endpoint)
  client = network.simple_party(submitter)

  @client.ledger_ready()
  def _add_rater(event):
    for master, _ in event.acs_find_active('Main.MovieRatings:Analyst').items():
      return (master.exercise("CreateRater", { "person": person, "personInfo": personInfo }))
  
  network.run_until_complete()


@mq.task
def submit_rating(submitter, endpoint, person, rating):
  network = Network()
  network.set_config(url = endpoint)
  client = network.simple_party(submitter)

  @client.ledger_ready()
  def _submit_rating(event):
    for master, _ in event.acs_find_active('Main.MovieRatings:Analyst').items():
      return (master.exercise("SubmitRating", { "person": person, "rating": rating }))
  
  network.run_until_complete()
