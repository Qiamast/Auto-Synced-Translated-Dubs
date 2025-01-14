#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Google Authentication Modules
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# Other Modules
import os
import sys
import traceback
from json import JSONDecodeError

TOKEN_FILE_NAME = 'token.pickle'

TTS_API = None
TRANSLATE_API = None

##########################################################################################
################################## AUTHORIZATION #########################################
##########################################################################################
# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the {{ Google Cloud Console }} at https://cloud.google.com/console
# Please ensure that you have enabled the Text to Speech API for your project.
# For more information about the client_secrets.json file format, see:
# https://developers.google.com/api-client-library/python/guide/aaa_client_secrets

# Authorize the request and store authorization credentials.
def get_authenticated_service():
  global TTS_API
  global TRANSLATE_API
  CLIENT_SECRETS_FILE = 'client_secrets.json'
  API_SCOPES = ['https://www.googleapis.com/auth/cloud-platform', 'https://www.googleapis.com/auth/cloud-translation']

  # TTS API Info
  TTS_API_SERVICE_NAME = 'texttospeech'
  TTS_API_VERSION = 'v1'
  TTS_DISCOVERY_SERVICE_URL = "https://texttospeech.googleapis.com/$discovery/rest?version=v1"

  # Translate API Info
  # https://translate.googleapis.com/$discovery/rest?version=v3 # v3 or beta v3beta1
  TRANSLATE_API_SERVICE_NAME = 'translate'
  TRANSLATE_API_VERSION = 'v3beta1'
  TRANSLATE_DISCOVERY_SERVICE_URL = "https://translate.googleapis.com/$discovery/rest?version=v3beta1"

  # Check if client_secrets.json file exists, if not give error
  if not os.path.exists(CLIENT_SECRETS_FILE):
    # In case people don't have file extension viewing enabled, they may add a redundant json extension
    if os.path.exists(f"{CLIENT_SECRETS_FILE}.json"):
      CLIENT_SECRETS_FILE = CLIENT_SECRETS_FILE + ".json"
    else:
      print(f"\n         ----- [!] Error: client_secrets.json file not found -----")
      print(f" ----- Did you create a Google Cloud Platform Project to access the API? ----- ")
      input("\nPress Enter to Exit...")
      sys.exit()

  creds = None
  # The file token.pickle stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first time.
  if os.path.exists(TOKEN_FILE_NAME):
    creds = Credentials.from_authorized_user_file(TOKEN_FILE_NAME, scopes=API_SCOPES)

  # If there are no (valid) credentials available, make the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      print(f"\nPlease login using the browser window that opened just now.\n")
      flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=API_SCOPES)
      creds = flow.run_local_server(port=0, authorization_prompt_message="Waiting for authorization. See message above.")
      print(f"[OK] Authorization Complete.")
      # Save the credentials for the next run
    with open(TOKEN_FILE_NAME, 'w') as token:
      token.write(creds.to_json())

  # Build tts and translate API objects    
  TTS_API = build(TTS_API_SERVICE_NAME, TTS_API_VERSION, credentials=creds, discoveryServiceUrl=TTS_DISCOVERY_SERVICE_URL)
  TRANSLATE_API = build(TRANSLATE_API_SERVICE_NAME, TRANSLATE_API_VERSION, credentials=creds, discoveryServiceUrl=TRANSLATE_DISCOVERY_SERVICE_URL)
  
  return TTS_API, TRANSLATE_API


def first_authentication():
  global TTS_API, TRANSLATE_API
  try:
    TTS_API, TRANSLATE_API = get_authenticated_service() # Create authentication object
  except JSONDecodeError as jx:
    print(f" [!!!] Error: " + str(jx))
    print(f"\nDid you make the client_secrets.json file yourself by copying and pasting into it, instead of downloading it?")
    print(f"You need to download the json file directly from the Google Cloud dashboard, by creating credentials.")
    input("Press Enter to Exit...")
    sys.exit()
  except Exception as e:
    if "invalid_grant" in str(e):
      print(f"[!] Invalid token - Requires Re-Authentication")
      os.remove(TOKEN_FILE_NAME)
      TTS_API, TRANSLATE_API = get_authenticated_service()
    else:
      print('\n')
      traceback.print_exc() # Prints traceback
      print("----------------")
      print(f"[!!!] Error: " + str(e))
      input(f"\nError: Something went wrong during authentication. Try deleting the token.pickle file. \nPress Enter to Exit...")
      sys.exit()
  return TTS_API, TRANSLATE_API
