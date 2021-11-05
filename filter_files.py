import json

from apiclient import errors
from google_api import GoogleAPI

# irá filtrar os arquivos a cada `step`
# exemplo:
#   Quando `start = 0`, `stop = 100` e `step = 10`
#   Então os filtros devem ser 0:10, 10:20, 20:30 ... 90:100
#
START = 0
STOP  = 1000
STEP = 100

# número maximo registros salvos no google_api.json
MAX_LENGTH = 1000

# arquivo de checkpoint do retorno
GOOGLE_API_JSON_FILE = 'google_api.json'

# suffixo dos arquivos que queremos mover
FILES_SUFFIX = ['aro', 'exp', 'lnd', 'val']

class FilterFiles:
  def __init__ (self):
    super().__init__()
    self.google_api = GoogleAPI()
    self.query = None

    with open(GOOGLE_API_JSON_FILE) as json_object:
      data = json.load(json_object)
      self.nextPageToken = data['nextPageToken']

  def show_metris(self, length):
    print('length: %d' % length)

  def save_files(self, items, nextPageToken):
    with open(GOOGLE_API_JSON_FILE) as json_object:
      data = json.load(json_object)
      data['nextPageToken'] = nextPageToken
      data['files'] += items

      self.show_metris(len(data['files']))
      
      with open(GOOGLE_API_JSON_FILE, 'w') as json_object:
        json.dump(data, json_object)

  def update_page_token(self, nextPageToken):
    self.nextPageToken = nextPageToken

  def start_by_filter(self):
    for i in range(round((STOP - START) / STEP) + 1):
      start = START + (i * STEP)
      stop = START + ((i + 1) * STEP)
      query = self.generate_query(start, stop)
      try:
        items, nextPageToken = self.google_api.list_files(query=query)
        if len(items) > 0:
          self.save_files(items, nextPageToken)
          self.update_page_token(nextPageToken)
        else:
          print('No files by filter.')
      except errors.HttpError as error:
        print('An error occurred: %s' % error)

  def generate_query(self, start, stop):
    filter_files = []
    for i in range(start, stop):
      for suffix in FILES_SUFFIX:
        filter_files.append("name = '%d_%s.npy'" % (i, suffix))
    return ' or '.join(filter_files)

  def start_by_limit(self):
    while True:
      try:
        items, nextPageToken = self.google_api.list_files(
          orderBy='name_natural',
          nextPageToken=self.nextPageToken
        )
        if len(items) == 0:
          break
        else:
          self.save_files(items, nextPageToken)
          self.update_page_token(nextPageToken)
          if len(items) == MAX_LENGTH:
            break
      except errors.HttpError as error:
        print('An error occurred: %s' % error)

if __name__ == '__main__':
  files_count = FilterFiles()
  files_count.start_by_filter()