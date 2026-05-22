import csv
import os
from users import login

file_name = 'hospital_tracker.csv'

def show_dashboard():

    if login():
        print("\n🏥 Hospital PRF Dashboard")
        print("-------------------------")

        if not os.path.isfile(file_name):
            print("No data found yet. Go to app.py to add some!")
            return

        total_count = 0
        stations = {}

        with open(file_name, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                total_count += 1
                stat = row['Station']
                stations[stat] = stations.get(stat, 0) + 1

        print(f"Total PRFs Collected: {total_count}")
        print("\nBreakdown by Station:")
        for stat, count in stations.items():
            print(f" {stat}: {count} forms")
        print("----------------------------\n")


show_dashboard()
