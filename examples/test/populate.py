
import requests
import json
import random

ENTRY_POINT = 'http://localhost:5000'


def post_person():
    person = [
        {
            'name': 'John',
            'age':10,
        },
        {
            'name': 'Serena',
            'age':10,
        },
        {
            'name': 'Mark',
            'age':10,
        },
    ]

    r = perform_post('person', json.dumps(person))
    print "'person' posted", r.status_code

    valids = []
    if r.status_code == 201:
        response = r.json()
        if response['_status'] == 'OK':
            for person in response['_items']:
                if person['_status'] == "OK":
                    valids.append(person['_id'])

    return valids

def perform_post(resource, data):
    headers = {'Content-Type': 'application/json'}
    return requests.post(endpoint(resource), data, headers=headers)


def delete():
    r = perform_delete('person')
    print "'person' deleted", r.status_code
    r = perform_delete('works')
    print "'works' deleted", r.status_code


def perform_delete(resource):
    return requests.delete(endpoint(resource))


def endpoint(resource):
    return '%s/%s/' % (ENTRY_POINT, resource)


def get():
    r = requests.get("%s/person/5439053fdaf985246a63a637"%ENTRY_POINT)
    print r.json()

if __name__ == '__main__':
    # post_person()
    get()
