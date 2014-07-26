import csv
from models import Store, Image
def upload():
    with open('ezchoice2.csv') as f:
        reader = csv.DictReader(f)
        for row in reader:
            s = Store()
            s.tags = row['tags']
            s.point = row['latlng']
            s.reference = row['reference'][0]

            for img in row['images']:
                img = Image()
                img.image = img
                img.tags = s.tags
                img.put()
                s.imgs.append(img)
