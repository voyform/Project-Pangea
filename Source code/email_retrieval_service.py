import base64
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle
from googleapiclient.discovery import build
import re
import requests
import json

# ERS is responsible for communicating with the gmail API and for overall backend activity of Project Pangea App
# creds and service
# creds and service

def get_credentials(CREDENTIALS_FILE_PATH, SCOPES):
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds


def list_emails(service, max_results=10):
    """
    lists selected (10) number of latests emails. Returns a list of subjects and ids
    """    
    results = service.users().messages().list(userId='me', maxResults=max_results).execute()
    messages = results.get('messages', [])
    if not messages:
        return 'No messages found'
    else:
        subjects = []
        msg_ids = []
        for message in messages:
            msg_id = message['id']
            msg = service.users().messages().get(userId='me', id=msg_id, format='metadata').execute()
            headers = msg['payload']['headers']
            subject = next((header['value'] for header in headers if header['name'] == 'Subject'), None)
            if subject:
                subjects.append(subject)
            if msg_id:
                msg_ids.append(msg_id)
        emails = {key: value for key, value in zip(msg_ids, subjects)}
        return emails


def get_email(service, msg_id):
    """
    returns a selected email (by email id) in its full json format
    """
    message = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    return message


def decode_text(text):
    """Decodes a URL-safe base64 encoded string."""
    try:
        # Decode URL-safe base64 encoding
        message = base64.urlsafe_b64decode(text)
        # Decode to utf-8
        return message.decode('utf-8')
    except Exception as e:
        # Handle exceptions that may occur during decoding
        print(f"Error decoding message: {e}")
        return None


def find_header(headers, name):
    """
    Finds and returns a header value from a list of headers
    """
    for header in headers:
        if header['name'] == name:
            return header['value']
    return None


def email_parser(email):
    """
    receives email data, extracts important information and returns it in a dict format 
    """
    encoded_body = email['payload']['parts'][1]['body']['data']
    decoded_body = decode_text(encoded_body)
    content = re.findall('>[^<]+<', decoded_body) #parsing the message for content
    # building the message
    build = []
    for item in content:
        build.append(item[1:-1])
    message = ''
    for item in build:
        message += ' ' + item # final, parsed message content             
    
    # getting sender and receiver info
    headers = email['payload']['headers']
    receiver = find_header(headers, 'To')
    sender = find_header(headers, 'From')
    date = find_header(headers, 'Date')

    #creating dict
    output = {
        'Message': message,
        'To': receiver,
        'From': sender,
        'Date': date
    }
    return output


def check_reputation(urls, api_token):
    """
    this function takes a list of URLs and checks their reputation with a Pangea API call, outputs a score for each URL
    """
    url = 'https://url-intel.aws.eu.pangea.cloud/v2/reputation' # URL of the reputation service

    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }
    
    # Data payload 
    data = {
        'urls': urls,  
        'provider': "crowdstrike",
    }

    # Convert dictionary to JSON format
    data_json = json.dumps(data)

    # Make the POST request
    response = requests.post(url, headers=headers, data=data_json)
    
    if response.status_code == 200 or response.status_code == 202: # status code 202 means we have received the URL where we can find the results
        data = response.json()  
        return data
    else:
        return {'error': f'Request failed with status code {response.status_code}'} # Return a dictionary with an error message if the request failed


def url_find(message):
    urls = re.findall('https?://[^ ]+', message)
    return urls


def request_response(location):
    """
    This function requests a response for a checked list of URLs
    """
    url = location # URL of the scan results 
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }
    # Make the GET request
    response = requests.get(url, headers=headers) # GET request
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()  
        return data
    else:
        return {'error': f'Request failed with status code {response.status_code}'} # Return a dictionary with an error message if the request failed


def check_urls(service, email_id):
    """
    receives an email id. Parses the email, decodes it and checks all the extracted urls, returning a dict with results from pangea URL Intel
    """
    message_body = email_parser(get_email(service, email_id))['Message'] # Get the text body of a message
    links = url_find(message_body) # extract the URLs
    response = check_reputation(links) # Check reputations of URLs extracted from the message
    if len(links) == 1: # if the list has > 1 links, the response will be available at the provided URL and has to be downloaded
        return response
    elif len(links) > 1:
        url = response['result']['location'] # the URL to the results from the scan
        bulk = request_response(url) # getting the results
        return bulk
    

def build_service():
    credentials = get_credentials() # logging to gmail's OAuth
    service = build('gmail', 'v1', credentials=credentials) # Building the service
    return credentials, service





