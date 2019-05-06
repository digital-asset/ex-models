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
