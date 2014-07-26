import csv
from models import Store, Image
import json
from google.appengine.ext import db

def upload():
    with open('ezchoice2.csv') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                s = Store()
                s.tags = json.loads(row['types'])
                s.point = db.GeoPt(*eval(row['latlng']))
                s.reference = row['reference'] and row['reference'][0] or ""
                
                for img in eval(row['images']):
                    image = Image()
                    image.image = img
                    image.tags = s.tags
                    image.put()
                    s.imgs.append(image)
            except Exception as e:
                pass
            finally:
                s.put()


upload()
