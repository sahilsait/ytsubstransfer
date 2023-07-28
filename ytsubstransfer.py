import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError

#Enter Channel ID of account you want to transfer subscriptions from here
CHANNEL1 = ''


def auth(credentialsJsonFileName, account):
    SCOPES = ["https://www.googleapis.com/auth/youtube"]
    creds = None
    if os.path.exists(f'token{account}`.json'):
        creds = Credentials.from_authorized_user_file(f'token{account}.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(f'{credentialsJsonFileName}', SCOPES)
            creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
    with open(f'token{account}.json', 'w') as token:
        token.write(creds.to_json())
    return creds


def getAllSubscriptions(channelId, creds):
    youtube = build('youtube', 'v3', credentials=creds)
    subscriptions = []
    nextPageToken = None
    while True:
        request = youtube.subscriptions().list(part='id,snippet', channelId=channelId, maxResults=50, pageToken=nextPageToken)
        response = request.execute()
        subscriptions.extend(response['items'])
        nextPageToken = response.get('nextPageToken')
        if not nextPageToken:
            break
    return subscriptions


def addSubscriptions(subscriptions, creds):
    youtube = build('youtube', 'v3', credentials=creds)
    for subscription in subscriptions:
        try:
            request = youtube.subscriptions().insert(
                part="snippet",
                body={
                    "snippet": {
                        "resourceId": {
                            "kind": "youtube#channel",
                            "channelId": subscription['snippet']['resourceId']['channelId']
                            }
                        }
                    }
                )
            response = request.execute()
        
        except HttpError as err:
            continue

    return response


if __name__ == '__main__':
    creds1 = auth('credentials.json', 1)
    subscriptions = getAllSubscriptions(CHANNEL1, creds=creds1)

    with open('subs.txt','w') as subs:
        for subscription in subscriptions:
            subs.write(subscription['snippet']['title'] + "\t")
            subs.write(subscription['snippet']['resourceId']['channelId'])
            subs.write("\n")

    creds2 = auth('credentials.json', 2)
    subscriptionResource = addSubscriptions(subscriptions, creds=creds2)