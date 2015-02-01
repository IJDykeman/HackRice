import time
import sqlite3
#from helpers import *
import groupy
import requests
import json

group = groupy.Group.create("hgh", description=None, image_url=None, share=True)


payload = {"members": [{"nickname": "Jameson","phone_number": "+1 3605367402","guid": "GUID-2"}]}
url = "https://api.groupme.com/v3/groups/{}/members/add?token=\"9432d9208be5013296de2e7fac077b2b\"".format(group.id)
#curl -X POST -H "Content-Type: application/json" -d '{"members": [{"nickname": "Jameson","phone_number": "+1 3605367402","guid": "GUID-2"}]}' https://api.groupme.com/v3/groups/12140525/members/add?token="9432d9208be5013296de2e7fac077b2b"

r = requests.post(url, data=payload)

if __name__=='__main__':
    print (r.text)



while(True):
	time.sleep(2)
	#print (get_agreement_map())