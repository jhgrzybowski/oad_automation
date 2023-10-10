import http.client
import json
import mimetypes
from codecs import encode

import requests


def create_user(firstName, lastName, mail, username):
    payload = {
      "firstName": firstName,
      "lastName": lastName,
      "email": mail,
      "enabled": 'true',
      "username": username
    }

    headers = {
      'Content-Type': 'application/json'
    }

    res = requests.post("http://localhost:8081/users/create", json=payload, headers=headers)

    print("adding user " + username + ", response: " + res.text)


def get_token(username):

    payload = 'grant_type=password&client_id=OAD&username=' + username +'&password=pass'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    res = requests.post("http://keycloak:8080/realms/once_a_day/protocol/openid-connect/token", payload, headers=headers)

    response_data = res.json()
    access_token = response_data.get('access_token')

    print("access token response: " + res.text)
    return access_token


def upload_photo(access_token, file_path):

    data_list = []
    boundary = 'wL36Yn8afVp8Ag7AmP8qZ0SA4n1v9T'
    data_list.append(encode('--' + boundary))
    data_list.append(encode('Content-Disposition: form-data; name=picture; filename={0}'.format(file_path)))

    file_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'

    data_list.append(encode('Content-Type: {}'.format(file_type)))
    data_list.append(encode(''))

    with open(file_path, 'rb') as f:
        data_list.append(f.read())

    data_list.append(encode('--' + boundary + '--'))
    data_list.append(encode(''))
    body = b'\r\n'.join(data_list)
    payload = body

    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-type': 'multipart/form-data; boundary={}'.format(boundary)
    }

    res = requests.post("http://localhost:8081/activities/picture", data=payload, headers=headers)

    print("adding pictures: " + res.text)


def main():

    create_user("adam", "nowak", "nowak@pg.edu.pl", "anowak")
    token = get_token("anowak")
    upload_photo(token, "photo.jpg")


if __name__ == '__main__':
    main()
