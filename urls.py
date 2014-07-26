
import webapp2
import sys
import logging

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'my-super-secret-key',
}

app = webapp2.WSGIApplication([
    (r'/explore', 'views.Explore'),
    (r'/recommend', 'views.Recommend'),
    (r'/detail', 'views.Detail'),

    (r'/postform', 'views.PostForm'),
    (r'/signupform', 'views.SignupForm'),
    
    (r'/signup', 'views.Signup'),
    (r'/login', 'views.Login'),
    (r'/logout', 'views.Logout'),
    (r'/post', 'views.Post'),
    (r'/post/list', 'views.Post'),
    (r'/post/(\w+)', 'views.Post'),
    (r'/logout', 'views.Logout'),
], debug=True, config=config)
