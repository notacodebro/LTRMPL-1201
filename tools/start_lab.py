#!/usr/bin/python3
import json
import requests
import urllib3

urllib3.disable_warnings()

def get_auth():
    _body = {'username' : 'admin', 'password' : 'cisco123!'}
    response = requests.post(url = f"{BASE_URL}/authenticate", json=_body, verify=False)
    return response.json()

def get_labs(headers):
    response = requests.get(url = f"{BASE_URL}/labs?show_all=true", headers=headers, verify=False)
    return response.json()

def get_lab_status(headers, lab_ids):
    lab_details = []
    for items in lab_ids:
        response = requests.get(url = f"{BASE_URL}/labs/{items}", headers=headers, verify=False)
        if response.json()['state'] == 'STOPPED':
            lab_details.append(response.json())
        else:
            pass
    return lab_details

def start_lab(status, headers):
    for items in status:
        if items['lab_title'] == 'SR - Minimal Lab':
       	    response = requests.put(url = f"{BASE_URL}/labs/{items['id']}/start", headers=headers, verify=False)
            print(response.status_code)
        else:
	    exit(1)    

def main():
    token = get_auth()
    headers = {'authorization' : f'Bearer {token}'}
    lab_ids = get_labs(headers)
    status = get_lab_status(headers, lab_ids)
    start_lab(status, headers)

BASE_URL = 'https://198.18.128.100/api/v0'
main()
