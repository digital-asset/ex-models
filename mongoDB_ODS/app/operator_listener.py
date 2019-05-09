# Copyright (c) 2019 Digital Asset (Switzerland) GmbH and/or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import getopt
import sys
import yaml
from dazl import simple_client, Network
from pymongo import MongoClient
from bson.errors import InvalidDocument
from types_translater import MongoDBTypesTranslater


def upsertIntoODS(db, dictionary, contractid, template, cdata):
  try:
    db[dictionary].insert_one({ 'contractId': str(contractid), 'contractType': str(template), 'payload': MongoDBTypesTranslater().translate(cdata) })
  except InvalidDocument as e:
    print("Insertion of contract " + str(contractid) + " failed; " + str(e))
    pass

translate
def removeFromODS(db, dictionary, contractid):
  try:
    db[dictionary].delete_one({ 'contractId': str(contractid) })
  except InvalidDocument as e:
    print("Deletion of contract " + str(contractid) + " failed; " + str(e))
    pass


if __name__ == '__main__':
  try:
    opts, _ = getopt.getopt(sys.argv[1:], "c:u:", ["config=", "user="])
  except getopt.GetoptError as e:
    print(e)
    exit(2)
  
  config_file = None
  listen_user = None

  for opt, arg in opts:
    if opt in ("-c", "--config"):
      config_file = arg
    elif opt in ("-u", "--user"):
      listen_user = arg
    else:
      print("Unknown option; exiting.")
      exit(3)

  if config_file == None or listen_user == None:
    print("Missing key arguments; exiting.")
    exit(4)

  with open(config_file, 'r') as stream:
    conf = yaml.safe_load(stream)
    dictionary = str(locals()['listen_user'] + '_acs')
    dh = MongoClient(conf['ods']['endpoint'])
    db = dh[conf['ods']['database']]
    db[dictionary].drop()

    network = Network()
    network.set_config(url = conf['ledger']['endpoint'])
    client = network.simple_party(listen_user)

    @client.ledger_ready()
    def print_initial_state(event):
      for key, val in event.acs_find_active('*').items():
        upsertIntoODS(db, dictionary, key, key.template_id, val)
        print("  [Active] ", key, ":", val)

    @client.ledger_create('*')
    def handle_create(event):
      upsertIntoODS(db, dictionary, event.cid, event.cid.template_id, event.cdata)
      print("  [Create] ", event.cid, event.cdata)

    @client.ledger_archive('*')
    def handle_archive(event):
      removeFromODS(db, dictionary, event.cid)
      print(" [Archive] ", event.cid, "has been archived.")

    network.run_forever()
