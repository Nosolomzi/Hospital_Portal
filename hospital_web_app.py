import csv
import os
from datetime import datetime
from users import login

file_name = 'hospital_tracker.csv'

def show_menu():
    print("\n" + "="*30)
    print("🏥 HOSPITAL PRF MASTER PORTAL")
    print("="*30)
    print("1. 📤 Upload New PRF")
    print("2. 📊 View Dashboard (Totals)")
    print("3. 🧾 Export Invoice for Excel")
    print("4. 🚪 Exit")
    return input("\nSelect an option (1-4): ")

def run_portal():
    if not login():
        return

    while True:
        choice = show_menu()

        if choice == '1':
            
            dist = input("Enter District (e.g. West Rand): ").upper()
            stat = input("Enter Station (e.g. Leratong): ").upper()
            inc = input("Enter Incident Number: ")
            
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
            print(f"\n SUCCESS! Saved to Batch: {batch}")

        elif choice == '2':
           
            if not os.path.isfile(file_name):
                print("\n⚠️ No data found yet.")
                continue
            
            with open(file_name, mode='r') as file:
                reader = csv.DictReader(file)
                data = list(reader)
                print(f"\n Total PRFs in System: {len(data)}")
                
                stats = {}
                for row in data:
                    s = row['Station']
                    stats[s] = stats.get(s, 0) + 1
                for s, count in stats.items():
                    print(f" {s}: {count} forms")

        elif choice == '3':
            
            if not os.path.isfile(file_name):
                print("\n⚠️ No data to export.")
                continue
            
            target = input("Enter the Batch ID to export: ").upper().strip()
            invoice_rows = []
            
            with open(file_name, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['Batch ID'] == target:
                        invoice_rows.append(row)
            
            if invoice_rows:
                export_name = f"Invoice_{target.replace(' ', '_')}.csv"
                with open(export_name, mode='w', newline='') as ex_file:
                    writer = csv.DictWriter(ex_file, fieldnames=invoice_rows[0].keys())
                    writer.writeheader()
                    writer.writerows(invoice_rows)
                print(f"\n Created: {export_name}")
            else:
                print("\n No records found for that ID.")

        elif choice == '4':
            print("Closing Portal. Stay safe!")
            break

if __name__ == "__main__":
    run_portal()

