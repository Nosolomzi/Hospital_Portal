import csv
import os
from datetime import datetime

file_name = 'hospital_tracker.csv'


print("🏥 HOSPITAL PRF PORTAL (Simple Version)")
print("---------------------------------------")
district = input("Enter District: ")
station  = input("Enter Station: ")
incident = input("Enter Incident Number: ")


now = datetime.now()
month_year = now.strftime("%b-%Y").upper()
batch_id = f"{district}_{station}_{month_year}_01".upper()
tracking_id = f"KMS-{now.strftime('%Y%m%d')}-{incident}-MID"
capture_date = now.strftime("%d-%b-%Y")

row_to_save = [incident, tracking_id, station.upper(), district.upper(), "Billable", batch_id, capture_date]
headers = ['Incident Number', 'Tracking ID', 'Station', 'District', 'Billing Class', 'Batch ID', 'Capture Date']


file_exists = os.path.isfile(file_name)

with open(file_name, mode='a', newline='') as file:
    writer = csv.writer(file)
    
    if not file_exists:
        writer.writerow(headers)

    writer.writerow(row_to_save)

print(f"\n SUCCESS! Data saved to {file_name}")

