#!/usr/bin/env python
""" Python Script to revoke users after a password change
This script is designed to revoke users from a Control Hub organization based on an INPUT CSV file with user emails or upn addresses.
The column names to be renamed in the csv as "email" and "upn" for respective user email address or upn addresses.
The script is designed to be executed by users with "full admin" role in the org.
Admin Access token can be obtained from https://developer.webex.com/docs/api/getting-started
Output file called Errors.csv is generated at the end in the same directory as the input CSV file 
Tested with Python version 3.9.12
"""

__author__ = "Ephraim Kakumani"
__date__ = "04/24/2023"

#############  Imports  #############
import requests
import json
import csv
import pandas as pd
import time
import os

#############  Definitions  #############
access_token = '' 
file_path = ''                                                   
auth_ids = []
get_auth_url = 'https://webexapis.com/v1/authorizations'                # Webex CH Get Authorizations Ids API URL
del_auth_url = 'https://webexapis.com/v1/authorizations/'               # Webex CH Delete Authorizations Ids API URL
gey_my_info_url = 'https://webexapis.com/v1/people/me'                  # Webex CH Get My Info API URL

#############  File Tasks  #############
if os.path.exists("Errors.csv"):
    os.remove("Errors.csv")

#############  Validate Access Token  #############
def get_access_token():
    global access_token
    access_token = ''
    while not access_token:
        access_token = input('Please enter your access token:  ')
        validationResponse = requests.get(gey_my_info_url, headers={'Authorization': 'Bearer ' + access_token})
        if validationResponse.status_code == 401:
            # This means the access token was invalid.
            print('Access Token was invalid.  Please check your access token was entered correctly and hasn\'t expired and try again below.\n')
            access_token = ''
    return access_token

#############  Retrieve User Authorization ID's #############
def retrieve_user_auth():
    global file_path
    global auth_ids
    auth_ids = []
    file_name = input('Enter CSV file name: ')
    file_path = os.path.abspath(file_name)
    df = pd.read_csv(file_name)
    user_email_addresses = df['email'].tolist()
    upn_email_addresses = df['upn'].tolist()

    # Merge User Email Address andUPN addresses
    email_addresses = user_email_addresses+upn_email_addresses

    # List Unique Email Address from User Email and UPN addresses
    unique_email_addresses = list(set(email_addresses))

    ### Retrieve all User Authorization ID's
    print('\n############# Begin retreiving User Authorization IDs #############\n')
    for email in unique_email_addresses:
        get_auth_email_url = get_auth_url+'?personEmail='+email
        headers = {'Authorization': 'Bearer ' + access_token, 
        'Content-Type': 'application/json'}
        querystring = {'personEmail': {email}}
        print(f'{get_auth_email_url}')
        response = requests.get(get_auth_url,headers=headers,params=querystring)
        error_message = 'GET Authorization'
        if response.status_code != 200 or len(response.json()['items']) == 0:
            # This means something went wrong.
            if response.status_code != 200:
                error_message = response.json()['message']
                print(f'HTTP Response: {response.status_code}, Message: {error_message}\n')
            else:
                print(f'No IDs listed for {email}\n')
            file_path = os.path.abspath('Errors.csv')
            with open(file_path,'a') as csvfile:
                csvfile.write(email + ',' + str(response.status_code) + ',' + error_message + '\n')
        else:
            get_auth_response_json = response.json()
            items = get_auth_response_json['items']
            for item in items:
                temp = item['id']
                auth_ids.append(temp)
            print(f'Email: {email}, Authorization ID: {auth_ids}\n')
    print('#############  End retreiving User Authorization IDs  #############\n\n')
    return auth_ids

#############  Revoke User Authorization ID's #############
def revoke_user_auth():
    print('#############  Begin revoking User Authorization IDs  #############\n')
    if not auth_ids:
        print('No User Authorization IDs to Revoke.\n')
    else:
        for item in auth_ids:
            del_email_auth_url = del_auth_url+item
            headers = {'Authorization': 'Bearer ' + access_token, 
            'Content-Type': 'application/json'}
            response = requests.delete(del_email_auth_url,headers=headers)
            error_message = 'Delete Authorization'
            if response.status_code != 204:
                error_message = response.json()['message']
                print(f'HTTP Response: {response.status_code}, Message: {error_message}, ID: {item}\n')
                file_path = os.path.abspath('Errors.csv')
                with open(file_path,'a') as csvfile:
                    csvfile.write(str(response.status_code) + ',' + error_message + '\n')
            else:
                print(f'User Revocation is successful - {item}\n')
    print('#############   End revoking User Authorization IDs   #############\n\n')

#############  Main Function #############
def main():
    get_access_token()
    retrieve_user_auth()
    revoke_user_auth()
    print('############# Note: Please check for the file Errors.csv if you encounter any errors. #############\n\n')
if __name__ == '__main__':
    main()