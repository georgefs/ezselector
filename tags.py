# -*- coding: utf-8 -*-

def SetTag(obj):
    import requests, urllib, json, re
    from models import Store
    print obj.name
    auth_info = {}
    auth_info['id'] = 'b5553f8dcedf9a1714aba4a7a9587411'  ##  api id
    auth_info['secret_key'] = '42f4f8c9e60147aa3358f1346cca1f13'  ##   api key
     
    resp = requests.post('http://api.ser.ideas.iii.org.tw/api/user/get_token', auth_info)
     
    token = json.loads(resp.content)['result']['token']
    api = 'http://api.ser.ideas.iii.org.tw:80/api/fb_checkin_search'
    data = {}
    data['coordinates']='23.5832, 120.5825'
    data['radius']='300'
    data['token']=token
    try:
        for i in re.split("[\s,./]", obj.name):
            print "    searching  ", i
            data['keyword'] = i
            resp = requests.post(api, data)
            dicData = json.loads(resp.content)
            if 'result' in dicData:
                for i in dicData['result']:
                    print "insert tag = " , i['category']
                    tag = i['category']
                    obj.tags.append(tag)
                    set(obj.tags)
                    obj.put()
            else:
               print "no results"
    except:
        print "finished"
            

def SetTags():
    import requests, urllib, json
    from models import Store
    query = Store.query().fetch(1000)
    for obj in query:
        SetTag(obj)
def test():
    import requests, urllib, json
     
    auth_info = {}
    auth_info['id'] = 'b5553f8dcedf9a1714aba4a7a9587411'  ##  api id
    auth_info['secret_key'] = '42f4f8c9e60147aa3358f1346cca1f13'  ##   api key
     
    resp = requests.post('http://api.ser.ideas.iii.org.tw/api/user/get_token', auth_info)
     
    token = json.loads(resp.content)['result']['token']
     
    api = 'http://api.ser.ideas.iii.org.tw/api/fb_checkin_search'
    data = {}
    data['coordinates']='23.5832, 120.5825'
    data['radius']='300'
    data['token']=token
    data['keyword'] = 'starbucks'
     
     
    resp = requests.post(api, data)
    dicData = json.loads(resp.content)
    import pdb; pdb.set_trace()
    if 'result' in dicData:
        for i in dicData['result']:
            i
        print dicData['result']
     
