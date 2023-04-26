# BulkUserRevocations
Python Script to Revoke Users in Bulk after a password change
  1. This script is designed to revoke users from a Control Hub organization based on an INPUT CSV file with user emails or upn addresses.
  2. The column names are named in the csv as "email" and "upn" for respective user email address or upn addresses.
  3. The script is designed to be executed by users with "full admin" role in the org.
  4. Admin Access token can be obtained from https://developer.webex.com/docs/api/getting-started
  5. Output file called Errors.csv is generated at the end in the same directory as the input CSV file.
  6. Tested with Python version 3.9.12
  
# Usage
Requires two inputs. Access token and name of the CSV file.

python3 BulkUserRevocationsv1.py


