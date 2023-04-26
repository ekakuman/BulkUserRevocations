# BulkUserRevocations
Python Script to Revoke Users in Bulk after a password change

This script is designed to revoke users from a Control Hub organization based on an INPUT CSV file with user emails or upn addresses.
The column names to be renamed in the csv as "email" and "upn" for respective user email address or upn addresses.
The script is designed to be executed by users with "full admin" role in the org.
Admin Access token can be obtained from https://developer.webex.com/docs/api/getting-started
Output file called Errors.csv is generated at the end in the same directory as the input CSV file 

Tested with Python version 3.9.12


