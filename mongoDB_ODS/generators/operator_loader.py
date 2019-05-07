import getopt
import sys
import yaml
from celery import Celery
import pandas as pd
import requests
import json
import datetime
import time
from dazl import Network, simple_client, create


def create_random_user(mq, url, userId, submitter, endpoint):
  response = requests.get(url)
    
  if response.status_code == 200:
    payload = json.loads(response.text)
    jsonResp = payload['results'][0]

    person = "p" + str(userId)
    personInfo = { 
      "name": {
        "title": { 
            (jsonResp['name']['title']).title(): {} 
        },
        "firstname": (jsonResp['name']['first']).title(),
        "lastname": (jsonResp['name']['last']).title()
      },
      "gender": {
        (jsonResp['gender']).title(): {}
      },
      "address": {
        "street": (jsonResp['location']['street']).title(),
        "city": (jsonResp['location']['city']).title(),
        "state": (jsonResp['location']['state']).title(),
        "postcode": jsonResp['location']['postcode']
      },
      "email": jsonResp['email'],
      "dob": (datetime.datetime.strptime(jsonResp['dob']['date'], "%Y-%m-%dT%H:%M:%SZ")).replace(tzinfo=datetime.timezone.utc)
    }

    mq.send_task('generators.submitter.add_rater', args = (submitter, endpoint, person, personInfo))
  else:
    create_random_user(mq, url, userId, submitter, endpoint)


def submit_rating(mq, rating, submitter, endpoint):
  rater = "p" + str(rating['userId'])
  ratingInfo = {
    "id": int(rating['movieId']),
    "rating": float(rating['rating']),
    "date": (datetime.datetime.strptime(
      time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(rating['timestamp'])),
      "%Y-%m-%dT%H:%M:%SZ")
    ).replace(tzinfo=datetime.timezone.utc),
    "name": rating['title'],
    "year": rating['year'],
    "genres": rating['genres'].split("|")
  }

  mq.send_task('generators.submitter.submit_rating', args = (submitter, endpoint, rater, ratingInfo))


if __name__ == "__main__":
  try:
    opts, _ = getopt.getopt(sys.argv[1:], "c:u:t:", ["config=", "user=", "test="])
  except getopt.GetoptError as e:
    print(e)
    exit(2)
  
  config_file = None
  submit_user = None
  test_elems = -1

  for opt, arg in opts:
    if opt in ("-c", "--config"):
      config_file = arg
    elif opt in ("-u", "--user"):
      submit_user = arg
    elif opt in ("-t", "--test"):
      test_elems = int(arg)
    else:
      print("Unknown option; exiting.")
      exit(3)

  if config_file == None or submit_user == None:
    print("Missing key arguments; exiting.")
    exit(4)

  with open(config_file, 'r') as stream:
    conf = yaml.safe_load(stream)
    network = Network()
    network.set_config(url = conf['ledger']['endpoint'])
    client = network.simple_party(submit_user)
    mq = Celery(broker = 'pyamqp://guest@localhost//')

    csvf_ratings = pd.read_csv(conf['generator']['ratings_file'])
    csvf_movies = pd.read_csv(conf['generator']['movies_file'])
    csvf_movies_split = csvf_movies['title'].str.split("(\d{4})", n = 1, expand = True)
    csvf_movies_title_clean = csvf_movies_split[0].str.split(" \($", n = 1, expand = True)
    csvf_movies['title'] = csvf_movies_title_clean[0]
    csvf_movies['year'] = csvf_movies_split[1]
    full_ratings_matrix = pd.merge(csvf_ratings, csvf_movies, on = "movieId")
    ratings = full_ratings_matrix if test_elems == -1 else full_ratings_matrix.sample(n = test_elems)
    uniqueUserIds = []

    @client.ledger_ready()
    def _add_analyst(event):
      if len(event.acs_find_active('Main.MovieRatings:Analyst')) == 0:
        return (create('Main.MovieRatings:Analyst', { "analyst": submit_user }))
    network.run_until_complete()

    for count in range(len(ratings)):
      rating = ratings.iloc[count]
      if rating['userId'] not in uniqueUserIds:
        create_random_user(mq, conf['generator']['users_url'], rating['userId'], submit_user, conf['ledger']['endpoint'])
        uniqueUserIds.append(rating['userId'])
      submit_rating(mq, rating, submit_user, conf['ledger']['endpoint'])
  
  print("Data load has been dispatched successfully, contracts will appear on the ledger asynchronously.")

