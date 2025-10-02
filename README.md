# Arknights_Scraper

NOT FOR PROFIT.
Email orpheus157@gmail.com if credentials do not work (as I am not sure how Google's credentials will work for external users.)

Usage (as of 10/2/2025):

quickstart.py:

Calculates approximate number of pulls that a player can accumulate by any given event date, starting on 9/20/2025.
Starting values are 114710 Orundum and 47 Headhunting Tickets.
Used to update [this Google Sheet](https://docs.google.com/spreadsheets/d/1r2O0kCwzh3_9ZERD1WnaEViZ10VFema5aizBdYyK_Ug/edit?usp=sharing).
Download quickstart.py, event_getter.py, and credentials.json.
Run "python quickstart.py".


ark_all_auto.py:
Calculates approximate number of pulls that a player can accumulate by any given event date, starting on current date.
Starting values are 0 Orundum and 0 Headhunting Tickets.
Used to update [this Google Sheet](https://docs.google.com/spreadsheets/d/182mhYXHd1GmehGzgd-wRTKXwlQY_A5qCy4tbW_oTTgY/edit?usp=sharing).
Download ark_all_auto.py, event_getter.py, and credentials.json.
Run "python ark_all_auto.py".

Notes:
Approximates Global Event dates by adding 166 days to CN Event dates.
Accounts for:
- 1700 Orundum per week for Annihilation missions
- 600 Orundum per month for certificate shop (awarded on the 1st of every month)
- 500 Orundum per week for weekly missions
- 100 Orundum per day for daily missions
- Free monthly card awarded on 10/8/2025 through 11/6/2025 (200 Orundum per day for the duration)
- 550 Orundum per day for two weeks per Limited Event (Celebration, Festival, Carnival)
- 5 Headhunting Tickets per month (from daily login and certificate shop, awarded on the 17th of every month)
- 3 Headhunting Tickets per Side Story or Intermezzo event shop
- 10 Headhunting Tickets per Limited Event (awarded on the first day)
- 1 Headhunting Ticket per day for two weeks per Limited Event (beginning on the first day)
