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

#############  Definitions  #############
accessToken = ''                                                    # Update this value to skip entering command line input
authIds = []
baseAuthURL = 'https://webexapis.com/v1/authorizations'             # Webex CH Authorization API base URL
getAuthURL = 'https://webexapis.com/v1/authorizations?personEmail=' # Webex CH Get Authorizations Ids API URL
delAuthURL = 'https://webexapis.com/v1/authorizations/'             # Webex CH Delete Authorizations Ids API URL
geyMyInfoURL = 'https://webexapis.com/v1/people/me'                 # Webex CH Get My Info API URL

#############  Validate Access Token  #############
def get_access_token():
    global accessToken
    accessToken = ''
    while not accessToken:
        accessToken = input('Please enter your access token:  ')
        validationResponse = requests.get(geyMyInfoURL, headers={'Authorization': 'Bearer ' + accessToken})
        if validationResponse.status_code == 401:
            # This means the access token was invalid.
            print('Access Token was invalid.  Please check your access token was entered correctly and hasn\'t expired and try again below.\n')
            accessToken = ''
    return accessToken

#############  Retrieve User Authorization ID's #############
def retrieve_user_auth():
    global authIds
    authIds = []
    file_name = input('Enter CSV file name: ')
    df = pd.read_csv(file_name)
    userEmailAddresses = df['email'].tolist()
    upnEmailAddresses = df['upn'].tolist()

    # Merge User Email Address andUPN addresses
    emailAddresses = userEmailAddresses+upnEmailAddresses

    # List Unique Email Address from User Email and UPN addresses
    uniqueemailAddresses = list(set(emailAddresses))

    ### Retrieve all User Authorization ID's
    for email in uniqueemailAddresses:
        getAuthEmailURL = getAuthURL+email
        headers = {'Authorization': 'Bearer ' + accessToken, 'Content-Type': 'application/json'}
        response = retry_request(getAuthEmailURL, headers)     
        error_message = 'GET Authorization API Call Error'
        handle_errors(response, error_message)
        getAuthResponseJson = response.json()
        if getAuthResponseJson.get('items'):
            items = getAuthResponseJson['items']
            for item in items:
                temp = item['id']
                authIds.append(temp)
        print(f'Email: {email}, Authorization ID: {authIds}\n')
    return authIds

#############  Revoke User Authorization ID's #############
def revoke_user_auth():
    if not authIds:
        print('No User Authorization IDs to Revoke.\n')
    else:
        for item in authIds:
            delEmailAuthURL = delAuthURL+item
            headers = {'Authorization': 'Bearer ' + accessToken, 'Content-Type': 'application/json'}
            response = retry_request(delEmailAuthURL, headers, method='DELETE')
            error_message = 'Delete Authorization API Call Error'
            handle_errors(response, error_message)
        print('User Revocation is successful.\n')

#############  Too Many Requests #############
def retry_request(url, headers, method='GET'):
    response = None
    while True:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        if response.status_code == 429:
            print('Webex returned a 429 response (too many API calls at once). Pausing script for 30 seconds...')
            time.sleep(30)
        else:
            break
    return response

#############  Error Handling #############
def handle_errors(response, error_message):
    if response.status_code not in (200, 400):
        print(f'Error: {error_message} {response.status_code}')
        error = response.json()['message']
        with open('Errors.csv','a') as csvfile:
            csvfile.write(str(response.status_code) + ',' + error + '\n')
        print(f'Please check for errors in the file Errors.csv.\n')
    else:
        print(f'\nProcessing...\n')

#############  Main Function #############
def main():
    get_access_token()
    retrieve_user_auth()
    revoke_user_auth()

if __name__ == '__main__':
    main()