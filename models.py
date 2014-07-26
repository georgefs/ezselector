import re
from google.appengine.api import images
import csv
import json
from google.appengine.ext import blobstore

def in_bound(ne, sw, point):
    max_lat, max_lng = ne
    min_lat, min_lng = sw
    lat, lng = point

    return max_lat > lat and min_lat < lat and max_lng > lng and min_lng < lng
   
def to_point(latlng):
    lat, lng = re.search('^\(\s*([\d.]+)\s*,\s*([\d.]+)\s*\)$', latlng).groups()
    return (float(lat), float(lng))



data = []
with open("source.csv", 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        row['latlng'] = to_point(row['latlng'])
        row['types'] = json.loads(row['types'])
        row['photos'] = json.loads(row['photos'])
        row['images'] = eval(row['images'])
        data.append(row)



from google.appengine.ext import ndb



class Image(ndb.Model):
    tag = ndb.StringProperty()
    image = ndb.StringProperty(indexed=False)
    cached_image = ndb.StringProperty(indexed=False)
    
    def create_cache(self):
        pass


class Store(ndb.Model):
    tags = ndb.StringProperty(repeated=True)
    name = ndb.StringProperty()
    point = ndb.GeoPtProperty()
    address = ndb.StringProperty(indexed=False)
    reference = ndb.StringProperty()
    imgs = ndb.StructuredProperty(Image, repeated=True)


class User(ndb.Model):
    name = ndb.StringProperty()
    email = ndb.StringProperty(indexed=False)
    password = ndb.StringProperty(indexed=False)
    mug_shot = ndb.BlobKeyProperty(indexed=False)

    def to_json(self):
        data = {}
        data['name'] = self.name
        data['email'] = self.email
        data['mug_shot'] = images.get_serving_url(self.mug_shot)
        return data   


class Message(ndb.Model):
    commit = ndb.StringProperty(indexed=False)
    author = ndb.StructuredProperty(User)
    updated = ndb.DateTimeProperty()

    def to_json(self):
        data = {}
        data['commit'] = self.commit
        data['author'] = self.author.to_json()
        data['updated'] = self.updated.strftime('%S000')
         


class Post(ndb.Model):
    author = ndb.StructuredProperty(User)
    commit = ndb.StringProperty(indexed=False)
    image = ndb.BlobKeyProperty(indexed=False)
    point = ndb.GeoPtProperty()
    msgs = ndb.StructuredProperty(Message, repeated=True)
    
    messages = ndb.StructuredProperty(Message, repeated=True)
    updated = ndb.DateTimeProperty()

    def to_json(self):
        data = {}
        data['author'] = self.author.to_json()
        data['image'] = images.get_serving_url(self.image)
        data['commit'] = self.commit
        data['point'] = self.point
        data['msgs'] = [msg.to_json() for msg in self.msgs]
        data['updated'] = self.updated.strftime('%S000')
        data['id'] = self.key().id()
        return data
    
