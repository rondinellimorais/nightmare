import json
import math
from thread import Th
from google_api import GoogleAPI

GOOGLE_API_JSON_FILE = 'google_api.frozen.json'

if __name__ == '__main__':
  n_threads = 5
  items = []
  google_api = GoogleAPI()

  with open(GOOGLE_API_JSON_FILE) as json_object:
    data = json.load(json_object)
    items = data['files']

  n_items_per_thread = math.ceil(len(items) / n_threads)
  for i in range(n_threads):
    start = i * n_items_per_thread
    stop = (i + 1) * n_items_per_thread
    chunk = items[start:stop]
    Th(google_api, chunk).start()