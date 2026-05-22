import csv
import os
from users import login

source_file = 'hospital_tracker.csv'

def create_invoice():
   
    if login():
        print("\n🧾 HOSPITAL INVOICE GENERATOR")
        print("------------------------------")
        
        if not os.path.isfile(source_file):
            print("No data found! Please run app.py first.")
            return

        batch_to_find = input("Enter the Batch ID to export: ").upper()
        
        invoice_data = []
        

        with open(source_file, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['Batch ID'] == batch_to_find:
                    invoice_data.append(row)


        if invoice_data:
            clean_name = batch_to_find.replace(" ", "_")
            export_name = f"Invoice_{clean_name}.csv"
            
            headers = invoice_data[0].keys()
            
            with open(export_name, mode='w', newline='') as export_file:
                writer = csv.DictWriter(export_file, fieldnames=headers)
                writer.writeheader()
                writer.writerows(invoice_data)
                
            print(f"\n SUCCESS! {len(invoice_data)} records exported to {export_name}")
        else:
            print(f"\n No records found for Batch ID: {batch_to_find}")


create_invoice()

