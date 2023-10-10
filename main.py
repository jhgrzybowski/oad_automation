import http.client
import json
import mimetypes
from codecs import encode

import requests


def create_user(firstName, lastName, mail, username):
    payload = json.dumps({
      "firstName": firstName,
      "lastName": lastName,
      "email": mail,
      "enabled": 'true',
      "username": username
    })

    headers = {
      'Content-Type': 'application/json'
    }

    res = requests.post("http://localhost:8081/users/create", json=payload, headers=headers)


    print(res)

# TODO: change http.client lib to requests
def get_token(username):
    conn = http.client.HTTPSConnection("keycloak", 8080)
    payload = 'grant_type=password&client_id=OAD&username=' + username +'&password=pass'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    conn.request("POST", "/realms/once_a_day/protocol/openid-connect/token", payload, headers)
    res = conn.getresponse()

    data = res.read()
    print(data.decode("utf-8"))

    json_data = json.load(data)
    acces_token = json_data.get('access_token', None)

    return acces_token


# TODO: change http.client lib to requests
def upload_photo(access_token, file_path):

    conn = http.client.HTTPSConnection("localhost", 8081)
    dataList = []
    boundary = 'wL36Yn8afVp8Ag7AmP8qZ0SA4n1v9T'
    dataList.append(encode('--' + boundary))
    dataList.append(encode('Content-Disposition: form-data; name=picture; filename={0}'.format(file_path)))

    fileType = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'

    dataList.append(encode('Content-Type: {}'.format(fileType)))
    dataList.append(encode(''))

    with open(file_path, 'rb') as f:
        dataList.append(f.read())
    dataList.append(encode('--' + boundary + '--'))
    dataList.append(encode(''))
    body = b'\r\n'.join(dataList)
    payload = body
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-type': 'multipart/form-data; boundary={}'.format(boundary)
    }
    conn.request("POST", "/activities/picture", payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))


def main():
    create_user("jan", "daciuk", "daciuk@pg.edu.pl", "jdaciuk")

if __name__ == '__main__':
    main()
