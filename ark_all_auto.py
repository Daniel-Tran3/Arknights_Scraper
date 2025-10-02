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
DAYS = 200
PULL_WRITE_RANGE = "Pulls_Auto!A1:H" + str(DAYS+1)
TICKETS_WRITE_RANGE = "Tickets_Auto!A1:H" + str(DAYS+1)
ORUNDUM_WRITE_RANGE = "Orundum_Auto!A1:J" + str(DAYS+1)
LIMITED = ["Celebration", "Festival", "Carnival"]
EVENT_TYPES = ["Side Story", "Intermezzo"]
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTHLY_CARD_STARTS = ["10/8/2025"]
MONTHLY_CARD_ENDS = ["11/6/2025"]

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

    pull_vals = []
    ticket_vals = []
    orundum_vals = []
    event_idx = 0
    monthly_card_idx = 0
    new_event = True
    today = datetime.datetime.today()
    starting_orundum = 0
    starting_tickets = 0

    # Add header row.
    pull_vals.append(["Date", "Day of Week", "Orundum", "Tickets", "Pulls", "Pulls Spent", "Pulls Tried", "Event Name"])
    ticket_vals.append(["Date", "Day of Week", "Tickets", "Spend", "Monthly", "Event Login", "Event Reward", "Event Name"])
    orundum_vals.append(["Date", "Day of Week", "Orundum", "Orundum Spend", "Daily", "Weekly", "Monthly", "Monthly Card", "Lottery", "Event Name"])

    # Non-header cell calculation for all three sheets.
    for i in range(DAYS):
      # Non-headers start on row 2
      row = i + 2

      # Get date info (All tables)
      curr_date = today + datetime.timedelta(days=i)
      day_of_week = WEEKDAYS[datetime.datetime.weekday(curr_date)]
      curr_date_str = curr_date.strftime("%m/%d/%Y")

      # Event Data (All tables)
      name = "N/A"

      # Pull sheet formulas
      pulls_orundum = f"=Orundum_Auto!C{row}"
      pulls_tickets = f"=Tickets_Auto!C{row}"
      pulls_pulls   = f"=FLOOR(C{row}/600) + D{row}"
      pulls_spent   = f"=Orundum_Auto!D{row}/600 + Tickets_Auto!D{row}"
      pulls_tried   = 0

      # Orundum sheet initial row (to avoid self-reference, formulas start after first row)
      orundum_orundum      = starting_orundum
      orundum_spend        = 0
      orundum_daily        = 0
      orundum_weekly       = 0
      orundum_monthly      = 0
      orundum_monthly_card = 0
      orundum_lottery      = 0

      # Tickets sheet initial row (also to avoid self-reference, formulas after first row)
      tickets_tickets   = starting_tickets
      tickets_spend     = 0
      tickets_monthly   = 0
      tickets_ev_login  = 0
      tickets_ev_reward = 0

      
      if (i > 0):
        # Orundum sheet formulas
        orundum_orundum = f"=C{row-1}+E{row}+F{row}+G{row}+H{row}+I{row}-D{row}"
        orundum_daily   = 100
        orundum_weekly  = f'=IF(EQ($B{row}, "Monday"), 2200, 0)'
        orundum_monthly = f"=IF(EQ(DAY(A{row}),1), 600, 0)"
        orundum_spend   = f"=MIN(600 * (Pulls_Auto!G{row} - Tickets_Auto!D{row}), FLOOR(C{row-1} / 600) * 600)"

        # Ticket sheet formulas
        tickets_tickets = f"=C{row-1}+E{row}+F{row}+G{row}-D{row}"
        tickets_monthly = f"=IF(EQ(DAY(A{row}),17), 5, 0)"
        tickets_spend   = f"=MIN(Pulls_Auto!G{row}, C{row-1})"
        

        # Monthly card
        if monthly_card_idx < len(MONTHLY_CARD_STARTS):
          curr_card_start = datetime.datetime.strptime(MONTHLY_CARD_STARTS[monthly_card_idx], "%m/%d/%Y")
          curr_card_end = datetime.datetime.strptime(MONTHLY_CARD_ENDS[monthly_card_idx], "%m/%d/%Y")
          if (curr_date >= curr_card_start and curr_date <= curr_card_end):
            orundum_monthly_card = orundum_monthly_card + 200
          if (curr_date == curr_card_end):
            monthly_card_idx = monthly_card_idx + 1
        # Event reward calculations (lottery, login, shop)
        if event_idx < len(event_list):
          if (curr_date >= event_list[event_idx][1] and curr_date <= event_list[event_idx][2]):
            name = event_list[event_idx][0]
            if (any(elem in name for elem in EVENT_TYPES)):
              if (curr_date == event_list[event_idx][1] or new_event):
                tickets_ev_reward = 3
              if (any(elem in name for elem in LIMITED)):
                if (curr_date == event_list[event_idx][1]):
                  tickets_ev_login = tickets_ev_login + 10
                if (curr_date <= event_list[event_idx][1] + datetime.timedelta(days=13)):
                  tickets_ev_login = tickets_ev_login + 1
                  orundum_lottery = orundum_lottery + 550
          new_event = False
          if (curr_date >= event_list[event_idx][2]):
            event_idx = event_idx + 1
            new_event = True
      pull_vals.append([curr_date_str, day_of_week, pulls_orundum, pulls_tickets, pulls_pulls, pulls_spent, pulls_tried, name])
      ticket_vals.append([curr_date_str, day_of_week, tickets_tickets, tickets_spend, tickets_monthly, tickets_ev_login, tickets_ev_reward, name])
      orundum_vals.append([curr_date_str, day_of_week, orundum_orundum, orundum_spend, orundum_daily, orundum_weekly, orundum_monthly, orundum_monthly_card, orundum_lottery, name])


    # Update Pulls Sheet
    result = (
        sheet.values()
        .update(
            spreadsheetId=SPREADSHEET_ID,
            range=PULL_WRITE_RANGE,
            valueInputOption="USER_ENTERED",
            body={"values": pull_vals})
        .execute()
    )
    print(f"{result.get('updatedCells')} cells updated.")
    
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
