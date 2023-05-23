from urllib.request import urlopen
import urllib 
import json
import pprint
import requests

from ckanapi import RemoteCKAN
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

api_key = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJDbDI2UGNXVldQZjhpZzgtV3FGUXlCc1R0Ql9yanA3M19MVzZWZERiT0FNIiwiaWF0IjoxNjg0Mzk1OTEyfQ.SyEx8IHt8KIxmnXKaUCj7E1Kqcev3O1QoM_VkX17dVA"

def POSTREQgetuserlist():
    data_dict = {}

    response = urlopen('http://localhost:5000/api/3/action/user_list')
    assert response.code == 200

    response_dict = json.loads(response.read())

    assert response_dict['success'] is True
    result = response_dict['result']

    # pprint.pprint(result)
    return result

def remoteCKANgetUserlist():
    demo = RemoteCKAN('http://localhost:5000', apikey = api_key)
    users = demo.action.user_list()
    return users
    
def toolkitgetUserlist():
    try: 
        result = toolkit.get_action("user_list")(context={'ignore_auth' : True})
        users = result['result']

        for user in users:
            print(user['name'])
    except Exception as e:
        print(f"API CALL FAILED ---------- {str(e)}")

def createAPItoken():
    usrlist = getuserlist()
    index = 0
    for i in range(len(usrlist)):
        if usrlist[i]['name'] == 'ckan_admin':
            # pprint.pprint(i)
            index = i
    sysadminID = usrlist[index]['id']
    print(sysadminID)
    payload = {
        "user" : sysadminID,
        "name" : "ckan_admin"
    }

    # response = urlopen('http://localhost:5000/api/3/action/api_token_create', json=payload)
    response = requests.post('http://localhost:5000/api/3/action/api_token_create', json=payload)
    if response.status_code == 200:
        api_key = response.json()["result"]
        print("API key created:", api_key)
    else:
        print("Failed to create API key. Status code:", response.status_code)
        print("Error message:", response.json()["error"])

def deleteuser():
    api_key = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJDbDI2UGNXVldQZjhpZzgtV3FGUXlCc1R0Ql9yanA3M19MVzZWZERiT0FNIiwiaWF0IjoxNjg0Mzk1OTEyfQ.SyEx8IHt8KIxmnXKaUCj7E1Kqcev3O1QoM_VkX17dVA"
    usrlist = getuserlist()
    index = 0
    for i in range(len(usrlist)):
        if usrlist[i]['name'] == 'test2':
            # pprint.pprint(i)
            index = i
    
    haoyiid = usrlist[index]['id']
    print(haoyiid)
    payload = {
        "id" : haoyiid 
    }

    headers = {
        "Authorization": api_key
    }

    response = requests.post('http://localhost:5000/api/3/action/user_delete', headers=headers ,data=payload)
    if response.status_code == 200:
        api_key = response.json()["result"]
        print("API key created:", api_key)
    else:
        print("Failed to create API key. Status code:", response.status_code)
        print("Error message:", response.json()["error"])

def get_admin():
    usrlist = POSTREQgetuserlist()
    index = 0
    for i in range(len(usrlist)):
        if usrlist[i]['name'] == 'ckan_admin':
            # pprint.pprint(i)
            index = i
    
    sysadmin = usrlist[index]['id']
    print(sysadmin)
    return sysadmin

if __name__ == "__main__":
    pprint.pprint(POSTREQgetuserlist())
    print()
    pprint.pprint(remoteCKANgetUserlist())
    print()
    toolkitgetUserlist()
