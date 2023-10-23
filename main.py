import csv
import io
import os
import random

from PIL import Image
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


def compress_photo(input_file_path, output_file_path, target_size, image_format):
    img = Image.open(input_file_path)

    quality = 95

    while True:
        img_io = io.BytesIO()
        img.save(img_io, format=image_format, quality=quality)
        img_size = img_io.tell()

        if img_size <= target_size or quality <= 10:
            break

        quality -= 5

    img.save(output_file_path, format=image_format, quality=quality)


def main():

    ############# SKRYPT DO KOMPRESJI ZDJEC #########################
    #
    # input_folder = "hobby_compressed"
    # output_folder = "images"
    # target_size = 700 * 700  # zmienic w zaleznosci ile sie chce pikseli
    #
    # for file_name in os.listdir(input_folder):
    #     input_path = os.path.join(input_folder, file_name)
    #
    #     if os.path.isfile(input_path):
    #         output_path = os.path.join(output_folder, file_name)
    #
    #     compress_photo(input_path, output_path, target_size, 'JPEG')
    #     print("skompresowano plik: " + file_name + "\n")
    #
    ##################################################################


    ########### SKRYPT DODAJACY UZYTKOWNIKA I WSTAWIAJACY ZDJECIA ######

    csv_file = "uzytkownicy_wybrani.csv"  # plik z danymi o uzytkownikach
    folder_path = "images"  # folder gdzie znajduja sie fotki

    with open(csv_file, 'r', newline='') as file:
        reader = csv.reader(file, delimiter=';')

        next(reader)  # pomijamy naglowek

        file_list = os.listdir(folder_path)

        users_to_add = 24  # ilu uzytkownikow chcemy dodac

        for i in range(users_to_add):
            row = next(reader)
            name, last_name, email, username = row
            print("creating user " + username)
            create_user(name, last_name, email, username)
            token = get_token(username)
            for j in range(4):
                random_file = random.choice(file_list)
                print("file he post is " + random_file)
                random_file_path = os.path.join('.\\', folder_path, random_file)
                print(random_file_path)
                upload_photo(token, random_file_path)
                file_list.remove(random_file)


if __name__ == '__main__':
    main()
