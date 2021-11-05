from threading import Thread
from google_api import GoogleAPI

class Th(Thread):
  def __init__ (self, google_api, items):
    Thread.__init__(self)
    self.items = items
    self.google_api: GoogleAPI = google_api

  def run(self):
    self.google_api.start(self.items)