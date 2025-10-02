import os.path
import event_getter
import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = "1r2O0kCwzh3_9ZERD1WnaEViZ10VFema5aizBdYyK_Ug"
READ_RANGE = "Tickets!A2:A200"
TICKETS_WRITE_RANGE = "Tickets!F2:H200"
ORUNDUM_WRITE_RANGE = "Orundum!I2:J200"
LIMITED = ["Celebration", "Festival", "Carnival"]
EVENT_TYPES = ["Side Story", "Intermezzo"]


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
    result = (
        sheet.values()
        .get(spreadsheetId=SPREADSHEET_ID, range=READ_RANGE)
        .execute()
    )
    values = result.get("values", [])

    if not values:
      print("No data found.")
      return


    event_list = event_getter.main()
    
    ticket_vals = []
    orundum_vals = []
    event_idx = 0
    new_event = True
    for i in range(len(values)):
      curr_date = datetime.datetime.strptime(values[i][0], "%m/%d/%Y")
      name = "N/A"
      event_shop = 0
      limited_free = 0
      lottery = 0
      if event_idx < len(event_list):
        if (curr_date >= event_list[event_idx][1] and curr_date <= event_list[event_idx][2]):
          name = event_list[event_idx][0]
          if (any(elem in name for elem in EVENT_TYPES)):
            if (curr_date == event_list[event_idx][1] or new_event):
              event_shop = 3
            if (any(elem in name for elem in LIMITED)):
              if (curr_date == event_list[event_idx][1]):
                limited_free = limited_free + 10
              if (curr_date <= event_list[event_idx][1] + datetime.timedelta(days=13)):
                limited_free = limited_free + 1
                lottery = lottery + 550
        new_event = False
        if (curr_date == event_list[event_idx][2]):
          event_idx = event_idx + 1
          new_event = True
      ticket_vals.append([limited_free, event_shop, name])
      orundum_vals.append([lottery, name])

    # Update HH Ticket Sheet
    result = (
        sheet.values()
        .update(
            spreadsheetId=SPREADSHEET_ID,
            range=TICKETS_WRITE_RANGE,
            valueInputOption="USER_ENTERED",
            body={"values": ticket_vals})
        .execute()
    )
    print(f"{result.get('updatedCells')} cells updated.")

    # Update Orundum Sheet
    result = (
        sheet.values()
        .update(
            spreadsheetId=SPREADSHEET_ID,
            range=ORUNDUM_WRITE_RANGE,
            valueInputOption="USER_ENTERED",
            body={"values": orundum_vals})
        .execute()
    )
    print(f"{result.get('updatedCells')} cells updated.")

  except HttpError as err:
    print(err)

  


if __name__ == "__main__":
  main()
