from google.appengine.datastore.datastore_query import Cursor
from models import Image
from share_libs.serve import cache_image
f = open('/tmp/cursor', 'w+')


imgs, cursor, more = Image.query().fetch_page(1000)
while True:
    try:
        imgs, cursor, more = Image.query().fetch_page(1000, start_cursor=cursor)
        f.write(cursor.urlsafe() +"\n")
        f.flush()
        print cursor
        for img in imgs:
            if not img.cached_image:
                try:
                    img.cached_image = cache_image(img.image).replace('localhost', '192.168.33.15')
                    print img.cached_image
                    img.put()
                except Exception as e:
                    print e
    except Exception as e:
        pass

