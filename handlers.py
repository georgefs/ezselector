from datetime import date, datetime
from webapp2_extras import sessions
from decimal import Decimal
import jinja2
import webapp2
import json
import base64
import os
import re
import urlparse

version_id = os.environ['CURRENT_VERSION_ID']
branch = version_id.split('.')[0]

class Error(Exception):
    pass

class PermissionDeniedError(Error):
    pass

def extend_json(obj):
    if isinstance(obj, date):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(obj, Decimal):
        return float(obj)


class HtmlHandler(webapp2.RequestHandler):
    jinja_environment = jinja2.Environment(
        loader=jinja2.FileSystemLoader('templates')
    )
    jinja_environment.globals['version_id'] = version_id
    jinja_environment.globals['branch'] = branch

    def HtmlResponse(self, template_path, data):
        template = self.jinja_environment.get_template(template_path)
        self.response.out.write(template.render(data))

    def handle_exception(self, exception, debug_mode):
        # notify.notify_req_error(True)

        if debug_mode:
            raise


class JsonHandler(webapp2.RequestHandler):

    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()


    """ extend json to support datetime, date, decimal """
    def JsonResponse(self, data, callback=None):
        callback = callback or self.request.get("callback")

        if self.app.debug:
            # pretty print
            data = json.dumps(data, indent=4, sort_keys=True, default=extend_json)
        else:
            # compressed
            data = json.dumps(data, separators=(',', ':'), default=extend_json)

        referer = self.request.headers.get('Referer')
        if referer:
            urlinfo = urlparse.urlparse(referer)
            if urlinfo.netloc.endswith('tagtooadex2.appspot.com') or urlinfo.netloc.startswith('localhost'):
                self.response.headers.update({'Access-Control-Allow-Origin': urlinfo.scheme+"://"+urlinfo.netloc})

        self.response.content_type="application/json"
        if callback:
            self.response.out.write("%s(%s);" % (callback, data))
        else:
            self.response.out.write(data)

    def format_exception(self, message, _type, code=None, status=400):
        code = code or _type

        self.response.set_status(status)
        self.JsonResponse({
            "error": {
                "message": message,
                "type": _type,
                "code": code
            }
        })

    def handle_exception(self, exception, debug):
        # try:
        #     notify.notify_req_error(True)
        # except:
        #     pass

        if isinstance(exception, AssertionError):
            self.format_exception(exception.message, "InvalidParameters")
        elif isinstance(exception, NotImplementedError):
            self.format_exception(exception.message, "InvalidOperation")
        elif isinstance(exception, PermissionDeniedError):
            self.format_exception(exception.message, "PermissionDenied")
        else:
            # if not debug:
            #     self.format_exception(exception.message, "Unknown", status=500)
            # else:
            raise


class ApiHandler(JsonHandler):
    def dispatch(self):
        allowed_list = ['219.85.68.183', '114.34.17.61']

        auth = self.request.headers.get("Authorization")

        if auth and auth == "Basic %s" % base64.b64encode("tagtoo:tagtoocusps") or self.request.remote_addr in allowed_list:
            return super(ApiHandler, self).dispatch()

        return self.handle_exception(PermissionDeniedError(), False)


class RestHandler(JsonHandler):
    def dispatch(self):
        """
            override the default dispatch process to add a pre process and post process
            http://webapp-improved.appspot.com/features.html#more-flexible-dispatching-mechanism
        """
        if self.request.get("_method") in ("GET", "POST", "PUT", "DELETE"):
            self.request.method = self.request.get("_method")

        return super(RestHandler, self).dispatch()

    def get(self, *args, **kwds):
        raise NotImplementedError()

    def post(self, *args, **kwds):
        raise NotImplementedError()

    def put(self, *args, **kwds):
        raise NotImplementedError()

    def delete(self, *args, **kwds):
        raise NotImplementedError()


