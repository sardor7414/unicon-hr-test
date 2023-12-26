import requests
import json
def create():
    response = requests.post(url='http://127.0.0.1:2305/api/sardortodo/',data={'member':1,'task':1,'organization':"Test",'photo':'test.png','latitude':123456,'longitude':123456})
    print(response.status_code)
create()