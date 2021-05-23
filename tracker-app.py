import time
from datetime import datetime
import win32gui
from tinydb import TinyDB, Query, where

# Configure timetracker db
db = TinyDB('timetracker-db.json')

# Frequency to capture screenshots
SCREENSHOT_FREQ = 60*1 # minutes

while True:
    now = datetime.now().strftime("%Y.%m.%d %H:%M:%S")
    time.sleep(SCREENSHOT_FREQ)   

    window = win32gui.GetForegroundWindow()
    active_window_name = win32gui.GetWindowText(window)

    print(now, active_window_name)
    db.insert({'datetime': now, 
               'active_window_name': active_window_name})