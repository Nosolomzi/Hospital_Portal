import csv
import os
from datetime import datetime
from users import login

file_name = 'hospital_tracker.csv'

def show_menu():
    print("\n" + "="*40)
    print("🏥 HOSPITAL PRF MASTER PORTAL v2.0")
    print("="*40)
    print("1. 📤 Upload New PRF (with Duplicate Check)")
    print("2. 📊 View Dashboard (Totals)")
    print("3. 🧾 Export Invoice for Excel")
    print("4. 🔍 Search for an Incident Number")
    print("5. 🚪 Exit")
    return input("\nSelect an option (1-5): ")

def run_portal():
    if not login():
        return

    while True:
        choice = show_menu()

        if choice == '1':
            # --- UPLOAD LOGIC ---
            inc = input("Enter Incident Number: ").strip()
            
            # DUPLICATE CHECK
            found = False
            if os.path.isfile(file_name):
                with open(file_name, mode='r') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        if row['Incident Number'] == inc:
                            found = True
                            break
            
            if found:
                print(f"\n❌ ERROR: Incident {inc} already exists in the system!")
                continue

            dist = input("Enter District: ").upper()
            stat = input("Enter Station: ").upper()
            now = datetime.now()
            batch = f"{dist}_{stat}_{now.strftime('%b-%Y')}_01".upper()
            
            file_exists = os.path.isfile(file_name)
            with open(file_name, mode='a', newline='') as file:
                headers = ['Incident Number', 'Station', 'District', 'Batch ID', 'Date']
                writer = csv.DictWriter(file, fieldnames=headers)
                if not file_exists:
                    writer.writeheader()
                writer.writerow({
                    'Incident Number': inc, 'Station': stat, 
                    'District': dist, 'Batch ID': batch, 
                    'Date': now.strftime("%d-%b-%Y")
                })
            print(f"\n✅ SUCCESS! Saved to Batch: {batch}")

        elif choice == '2':
            if not os.path.isfile(file_name):
                print("\n⚠️ No data found yet.")
                continue
            with open(file_name, mode='r') as file:
                data = list(csv.DictReader(file))
                print(f"\n📊 Total PRFs: {len(data)}")
                stats = {}
                for row in data:
                    s = row['Station']
                    stats[s] = stats.get(s, 0) + 1
                for s, count in stats.items():
                    print(f"📍 {s}: {count} forms")

        elif choice == '3':
            if not os.path.isfile(file_name):
                print("\n⚠️ No data to export.")
                continue
            target = input("Enter Batch ID: ").upper().strip()
            rows = []
            with open(file_name, mode='r') as file:
                for row in csv.DictReader(file):
                    if row['Batch ID'] == target:
                        rows.append(row)
            if rows:
                name = f"Invoice_{target}.csv"
                with open(name, mode='w', newline='') as f:
                    w = csv.DictWriter(f, fieldnames=rows[0].keys())
                    w.writeheader()
                    w.writerows(rows)
                print(f"\n✅ Created: {name}")
            else:
                print("\n❌ Batch not found.")

        elif choice == '4':
            # --- SEARCH LOGIC ---
            search_id = input("Enter Incident Number to find: ").strip()
            found_record = None
            if os.path.isfile(file_name):
                with open(file_name, mode='r') as file:
                    for row in csv.DictReader(file):
                        if row['Incident Number'] == search_id:
                            found_record = row
                            break
            
            if found_record:
                print("\n🔎 RECORD FOUND:")
                for key, value in found_record.items():
                    print(f"{key}: {value}")
            else:
                print(f"\n❌ No record found for Incident {search_id}")

        elif choice == '5':
            print("Closing Portal. Stay safe!")
            break

if __name__ == "__main__":
    run_portal()