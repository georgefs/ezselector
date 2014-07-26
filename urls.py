
import webapp2
import sys
import logging

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'my-super-secret-key',
}

app = webapp2.WSGIApplication([
    (r'/explore/?', 'views.Explore'),
    (r'/recommend/?', 'views.Recommend'),
    (r'/detail/?', 'views.Detail'),

    (r'/explore2/?', 'api.Explore'),
    (r'/recommend2/?', 'api.Recommend'),
    (r'/detail2/?', 'api.Detail'),

    (r'/postform/?', 'views.PostForm'),
    (r'/signupform/?', 'views.SignupForm'),
    
    (r'/signup/?', 'views.Signup'),
    (r'/login/?', 'views.Login'),
    (r'/logout/?', 'views.Logout'),
    (r'/post/?', 'views.Post'),
    (r'/post/list/?', 'views.Post'),
    (r'/post/(\d+)/?', 'views.Post'),
    (r'/logout/?', 'views.Logout'),
    (r'/preview/?', 'views.Preview'),
    (r'/message/?', 'views.Message'),
    (r'/images/(\d+)/?', 'views.ImageHandler'),
    (r'/store/(\d+)/?', 'views.StoreHandler'),
], debug=True, config=config)
