from handlers import JsonHandler
from google.appengine.api import images
from webapp2_extras import sessions
import json
import csv
import copy
from models import data, in_bound, to_point, User, Message, Post
import random
import logging
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
static_map = "http://maps.googleapis.com/maps/api/staticmap?center={0},{1}&zoom=17&size=200x200&markers=color:red%7Ccolor:red%7Clabel:A%7C{0},{1}"



dis = 500000 * 11 * 1e-6
class Explore(JsonHandler):
    def get(self, *args, **kwargs):
        tags = self.request.get('tags', '[]')
        tags = json.loads(tags)

        size = self.request.get_range('size') or 6

        latlng = self.request.get('latlng', '(25, 121)')
        latlng = to_point(latlng)
        ne = tuple([v+dis for v in latlng])
        sw = tuple([v-dis for v in latlng])
        result = filter(lambda d:in_bound(ne, sw, d['latlng']), data)
        random.shuffle(result)
        result = result[:size]
        result = copy.deepcopy(result)
        for r in result:
            r['img'] = random.choice([img for img in r['images'] if 'map' not in img])
            r['tags'] = r.pop('types')
            r['img_id'] = "img_"+r.pop('id')
            if r.get('images', False):
                del r['images']
                del r['photos']
                del r['place_id']
                del r['name']
                del r['address']
                del r['scope']

        self.JsonResponse(result)


class Recommend(JsonHandler):
    def get(self, *args, **kwargs):
        tags = self.request.get('tags', '[]')
        tags = json.loads(tags)

        size = self.request.get_range('size') or 6

        latlng = self.request.get('latlng', '(25, 121)')
        latlng = to_point(latlng)
        ne = tuple([v+dis for v in latlng])
        sw = tuple([v-dis for v in latlng])
        result = filter(lambda d:in_bound(ne, sw, d['latlng']), data)
        random.shuffle(result)
        result = result[:size]

        result = copy.deepcopy(result)
        for r in result:
            r['img'] = random.choice([img for img in r['images'] if 'map' not in img])
            r['tags'] = r.pop('types')
            if r.get('images', False):
                del r['images']
                del r['place_id']
                del r['scope']

        self.JsonResponse(result)


class Detail(JsonHandler):
    def get(self, *args, **kwargs):
        _id = self.request.get('id')
        logging.info(data[:10])
        result = filter(lambda d:d['id'] == _id, data)[0]
        result = copy.deepcopy(result)
        result['static_map'] = static_map.format(*result['latlng'])
        result['price_level'] = random.choice(range(1,6))
        if result.get('scope', False):
            del result['scope'] 
        if result.get('place_id', False):
            del result['place_id']
        result['logo'] = result['photos'] and result[0]
        self.JsonResponse(result)


class Login(JsonHandler):
    def get(self):
        email = self.request.get('email')
        password = self.request.get('password')

        user = User.get_by_id(email)
        if not user or password != user.password:
            self.JsonResponse({"STATUS": "ERROR", "MSG":"LOGIN ERROR"})
        else:
            self.session['user'] = user.to_json()
            self.JsonResponse({"STATUS": "SUCCESS"})



            
class Logout(JsonHandler):
    def get(self):
        import pdb;pdb.set_trace()
        self.session['user'] = None


class Signup(blobstore_handlers.BlobstoreUploadHandler, JsonHandler):
    def post(self):
        name = self.request.get('name')
        email = self.request.get('email')
        password = self.request.get('password')
        mug_shot = self.get_uploads('mug_shot')[0].key()
        if User.get_by_id(email):
            self.JsonResponse({"STATUS": "ERROR", "MSG":"EMAIL REPEAT"})
            return            

        user = User(id=email)
        user.name = name
        user.email = email
        user.password = password
        user.mug_shot = mug_shot
        user.put()
        self.JsonResponse({"STATUS": "SUCCESS"})


class SignupForm(JsonHandler):
    def get(self):
        template = '''
            <html>
                <body>
                    <form action="{}" method="POST" enctype="multipart/form-data">
                        Name: <input  name="name"><br> 
                        email: <input  name="email"><br> 
                        password: <input  name="password"><br> 
                        Upload File: <input type="file" name="mug_shot"><br> 
                        <input type="submit" name="submit" value="Submit"> 
                    </form>
                </body>
            </html>

        '''
        upload_url = blobstore.create_upload_url('/signup')
        self.response.out.write(template.format(upload_url))

class PostForm(JsonHandler):
    def get(self):
        template = '''
            <html>
                <body>
                    <form action="{}" method="POST" enctype="multipart/form-data">
                        commit: <input  name="commit"><br> 
                        Upload File: <input type="file" name="image"><br> 
                        <input type="submit" name="submit" value="Submit"> 
                    </form>
                </body>
            </html>

        '''
        upload_url = blobstore.create_upload_url('/post')
        self.response.out.write(template.format(upload_url))


class Post(JsonHandler):
    
    def get(self, _id=None):
        size = self.request.get_range('size') or 10
        cursor = self.request.get('cursor') or None

        if not _id:
            posts, next_curs, more = Post.query().fetch_page(size, start_cursor=cursor)
        elif _id == 'me':
            posts, next_curs, more = Post.query(author=User.get_by_id(self.session['user'].email)).fetch_page(size, start_cursor=cursor)
        else:
            posts = [Post.get_by_id(_id)]
            next_curs = None
            more = False
        
        posts = [post.to_json() for post in posts]
        
        self.JsonResponse({"posts":posts, "more":more, "next_cursor": next_cursor})
            
        
    def post(self):
        post = Post()
        post.author = User.get_by_id(self.session['user'].email)
        assert author
        post.commit = self.request.get('commit')
        post.image = self.get_uploads('image')[0].key()
        post.put()
        
        self.JsonResponse({"STATUS": "SUCCESS"})

class Message(JsonHandler):
    def post(self):
        post_id = self.request.get('post_id')
        commit = self.request.get('commit')
        user = User.get_by_id(self.session['user'].email)
        assert user

        post = Post.get_by_id(post_id)
        msg = Message()
        msg.author = user
        msg.commit = commit
        
        msg.put()
        post.msgs.append(msg)
        post.put()
