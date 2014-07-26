from google.appengine.datastore.datastore_query import Cursor
from models import Image
from share_libs.serve import cache_image



imgs, cursor, more = Image.query().fetch_page(100)
while True:
    imgs, cursor, more = Image.query().fetch_page(100, start_cursor=cursor)
    for img in imgs:
        if not img.cached_image:
            try:
                img.cached_image = cache_image(img.image).replace('localhost', '192.168.33.15')
                print img.cached_image
                img.put()
            except Exception as e:
                print e

