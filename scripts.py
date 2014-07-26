import csv
from models import Store, Image
import json
from google.appengine.ext import db
import re

def upload():
    with open('ezchoice.csv') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                s = Store()
                
                print row['name'], row['images'], row['types']
                if re.search("\[.*\]", row['reference']):
                    row['place_id'] = row['scope']
                    row['scope'] = row['latlng']
                    row['latlng'] = row['address']
                    row['address'] = row['photos']
                    row['photos'] = row['reference']

            

                print row['name'], row['images'], row['types']
                s.tags = json.loads(row['types'])
                s.point = db.GeoPt(*eval(row['latlng']))
                s.reference = row['reference'] and row['reference'][0] or ""
                s.address = row['address']
                s.name = row['name']

                
                for img in eval(row['images']):
                    image = Image()
                    image.image = img
                    image.put()
                    s.imgs.append(image)
            except Exception as e:
                pass
            finally:
                s.put()


upload()
