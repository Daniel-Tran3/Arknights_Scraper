import os.path
import event_getter
import datetime
import pandas as pd

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = "182mhYXHd1GmehGzgd-wRTKXwlQY_A5qCy4tbW_oTTgY"
PULL_DATE_CSV = "pull_dates.csv"
INIT_VALS_CSV = "starting_vals.csv"

def main():
  """Shows basic usage of the Sheets API.
  Prints values from a sample spreadsheet.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("sheets", "v4", credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()

    event_list = event_getter.main()
    pull_date_df = pd.read_csv(PULL_DATE_CSV)
    starting_vals_df = pd.read_csv(INIT_VALS_CSV)

    pull_dates = len(pull_date_df)
    pull_date_write_range="User_Values!A2:B" + str(pull_dates+1)
    starting_vals_write_range="User_Values!D2:E2"

    # Pull Date Values From CSV
    pull_date_vals = []
    for i in range(pull_dates):
      pull_date_vals.append([str(pull_date_df.iloc[i].iloc[0]), str(pull_date_df.iloc[i].iloc[1])])
    
    # Starting Values From CSV
    starting_vals = []
    starting_vals.append([str(starting_vals_df.iloc[0][0]), str(starting_vals_df.iloc[0][1])])

    # Update Pull Date Values On Sheet
    result = (
        sheet.values()
        .update(
            spreadsheetId=SPREADSHEET_ID,
            range=pull_date_write_range,
            valueInputOption="USER_ENTERED",
            body={"values": pull_date_vals})
        .execute()
    )
    print(f"{result.get('updatedCells')} cells updated.")

    # Update Starting Values On Sheet
    result = (
        sheet.values()
        .update(
            spreadsheetId=SPREADSHEET_ID,
            range=starting_vals_write_range,
            valueInputOption="USER_ENTERED",
            body={"values": starting_vals})
        .execute()
    )
    print(f"{result.get('updatedCells')} cells updated.")

  except HttpError as err:
    print(err)

  


if __name__ == "__main__":
  main()
