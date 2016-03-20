# Code based on the Hello Analytics program which can be found online 
# at: https://developers.google.com/analytics/devguides/config/mgmt/v3/quickstart/service-py

"""A simple example of how to access the Google Analytics API."""
from flask import Flask

import argparse

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools

import json
import re
import os

app = Flask(__name__)

@app.route("/")
def hello_world():
    # Define the auth scopes to request.
    scope = ['https://www.googleapis.com/auth/analytics.readonly']

    # Use the developer console and replace the values with your
    # service account email and relative location of your key file.
    service_account_email = 'osulld13@sunny-inn-125021.iam.gserviceaccount.com'
    key_file_location = '/var/www/FlaskApp/FlaskApp/MyProject-dbb9c292fd5e.p12'

    # Authenticate and construct service.
    service = get_service('analytics', 'v3', scope, key_file_location, service_account_email)
    profile = get_first_profile_id(service)
    result = format_top_content(get_top_content(service, profile))
    return result

def get_service(api_name, api_version, scope, key_file_location,
                service_account_email):
  """Get a service that communicates to a Google API.

  Args:
    api_name: The name of the api to connect to.
    api_version: The api version to connect to.
    scope: A list auth scopes to authorize for the application.
    key_file_location: The path to a valid service account p12 key file.
    service_account_email: The service account email address.

  Returns:
    A service that is connected to the specified API.
  """

  credentials = ServiceAccountCredentials.from_p12_keyfile(service_account_email, key_file_location, scopes=scope)

  http = credentials.authorize(httplib2.Http())

  # Build the service object.
  service = build(api_name, api_version, http=http)

  return service

def get_first_profile_id(service):
  # Use the Analytics service object to get the first profile id.

  # Get a list of all Google Analytics accounts for this user
  accounts = service.management().accounts().list().execute()

  if accounts.get('items'):
    # Get the first Google Analytics account.
    account = accounts.get('items')[0].get('id')

    # Get a list of all the properties for the first account.
    properties = service.management().webproperties().list(
        accountId=account).execute()

    if properties.get('items'):
      # Get the first property id.
      property = properties.get('items')[0].get('id')

      # Get a list of all views (profiles) for the first property.
      profiles = service.management().profiles().list(
          accountId=account,
          webPropertyId=property).execute()

      if profiles.get('items'):
        # return the first view (profile) id.
        return profiles.get('items')[0].get('id')

  return None

# dimensions=ga:pagePath
# metrics=ga:pageviews,ga:uniquePageviews,ga:timeOnPage,ga:bounces,ga:entrances,ga:exits
# sort=-ga:pageviews

def get_top_content(service, profile_id):
  # Use the Analytics Service Object to query the Core Reporting API
  # for the top requested objects in the last 7 days
  return service.data().ga().get(
      ids='ga:' + profile_id,
      start_date='7daysAgo',
      end_date='today',
      dimensions='ga:pagePath',
      metrics='ga:pageviews,ga:uniquePageviews,ga:timeOnPage,ga:bounces,ga:entrances,ga:exits',
      sort='ga:pageviews').execute()

def print_top_content(results):
  # Print data nicely for the user.
  if results:
    print 'View (Profile): %s' % results.get('profileInfo').get('profileName')

    i = 1
    for result in results.get('rows'):
      print 'Content %d: %s' % (i, result[0])
      i = i + 1

def format_top_content(results):
  # organise data nicely for the user.
  if results:
    # an ordered list of the results
    result_list = []
    pattern = '/home/#folder_id=(.*)&pidtopage=(.*)&entry_point=([0-1]*)';
    template = re.compile(pattern)
    rank = 1
    for result in results.get('rows'):
      match = template.search(result[0])
      if match:
          object = {'folder_id': match.group(1), 'pid': match.group(2)}
          result_list.append(object)
          rank = rank + 1

    formatted_result = {'objects':result_list}
    return json.dumps(formatted_result, separators=(',',':'))

  else:
    print 'No results found'

if __name__ == "__main__":
    app.run()
