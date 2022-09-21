import requests
import json

url = 'http://localhost:8088/chatbot/echo'
myobj = {'somekey':'somevalue'}
send_json = json.dumps(myobj)
x = requests.post(url, data=send_json)
json_res = x.text
res = json.loads(json_res)
print(res)