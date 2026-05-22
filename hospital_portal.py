import csv
import os
from datetime import datetime

# --- 1. FULL DATABASE FROM YOUR PHOTO ---
DISTRICTS = {
    "CITY OF TSHWANE": ["Mamelodi", "Block JJ", "Odi", "Kalafong", "Cullinan", "Prinshof", "Temba", "Laudium", "Dr George Mukhari", "Bronkhorstspruit", "Ekangala"],
    "WESTRAND": ["Bekkersdal", "Carltonville", "Dr Yusuf Dadoo", "Fochville", "Khutsong", "Leratong", "Magalies", "Mohlakeng/Randfontein", "Sterkfontein", "Wedela", "Westonaria"],
    "CITY OF JOHANNESBURG": ["Alexandra", "Bara/Eldorado", "Chiawelo", "Diepsloot/OR Tambo", "Discovery", "Ebony Park", "Edenvale", "Eldorado Park", "Hillbrow", "Imbalenhle/Orange Farm", "Lenasia", "Lenasia South", "Midrand", "Mofolo", "Orlando East", "Selby", "Tsepo Temba", "Witkoppen/Tara", "Zola"],
    "CITY OF EKURHULENI": ["Bertha Gxowa/Germiston", "Phola Park/Botshelong", "Daggafontein/Springs", "Devon", "Dun Swart", "Far East Rand", "Goba/Lluthundweni", "Itereleng", "Nokuthela Ngwenya", "Phillip Moyo", "Pholosong", "Tambo Memorial", "Thelle Mogoerane", "Thembisa"],
    "SEDIBENG": ["Evaton", "Heidelberg", "Meyerton/Pontshong", "Sebokeng", "Vanderbijlpark/J Heyns", "Vereeniging"]
}

FILE_NAME = 'hospital_tracker.csv'

def main_menu():
    print("\n" + "="*40)
    print("🏥 GAUTENG HEALTH: PRF PORTAL")
    print("="*40)
    print("1. 📤 Capture New PRF")
    print("2. 🔍 Search Incident Number")
    print("3. 📊 View All Records")
    print("4. 🧾 Export Batch to Excel")
    print("5. 🚪 Exit")
    return input("\nSelect Option (1-5): ")

def run_portal():
    while True:
        choice = main_menu()

        if choice == '1':
            # SELECT DISTRICT
            d_keys = list(DISTRICTS.keys())
            print("\n--- SELECT DISTRICT ---")
            for i, d in enumerate(d_keys, 1): print(f"{i}. {d}")
            d_idx = int(input("Number: ")) - 1
            sel_dist = d_keys[d_idx]

            # SELECT STATION
            s_list = DISTRICTS[sel_dist]
            print(f"\n--- STATIONS IN {sel_dist} ---")
            for i, s in enumerate(s_list, 1): print(f"{i}. {s}")
            s_idx = int(input("Number: ")) - 1
            sel_stat = s_list[s_idx]

            inc = input("\nEnter Incident Number: ").strip()
            
            # SAVE DATA
            now = datetime.now()
            batch = f"{sel_dist}_{sel_stat}_{now.strftime('%b-%Y')}_01".upper().replace(" ", "_")
            
            exists = os.path.isfile(FILE_NAME)
            with open(FILE_NAME, 'a', newline='') as f:
                w = csv.DictWriter(f, fieldnames=['Incident', 'Station', 'District', 'Batch ID', 'Date'])
                if not exists: w.writeheader()
                w.writerow({'Incident': inc, 'Station': sel_stat, 'District': sel_dist, 'Batch ID': batch, 'Date': now.strftime("%d-%b-%Y")})
            print(f"\n✅ SUCCESS: Saved to {batch}")

        elif choice == '2':
            search_id = input("\nEnter Incident Number to find: ").strip()
            found = False
            if os.path.exists(FILE_NAME):
                with open(FILE_NAME, 'r') as f:
                    for row in csv.DictReader(f):
                        if row['Incident'] == search_id:
                            print(f"\n🔎 FOUND: {row}")
                            found = True; break
            if not found: print("\n❌ No record found.")

        elif choice == '3':
            if os.path.exists(FILE_NAME):
                with open(FILE_NAME, 'r') as f:
                    data = list(csv.DictReader(f))
                    print(f"\n📊 Total Records: {len(data)}")
                    for r in data: print(f"{r['Date']} | {r['Station']} | {r['Incident']}")
            else: print("\n⚠️ No data yet.")

        elif choice == '4':
            target = input("\nEnter Batch ID to Export: ").upper().strip()
            rows = []
            if os.path.exists(FILE_NAME):
                with open(FILE_NAME, 'r') as f:
                    for row in csv.DictReader(f):
                        if row['Batch ID'] == target: rows.append(row)
            if rows:
                out_name = f"Invoice_{target}.csv"
                with open(out_name, 'w', newline='') as f:
                    w = csv.DictWriter(f, fieldnames=rows[0].keys())
                    w.writeheader(); w.writerows(rows)
                print(f"\n✅ EXPORTED: {out_name}")
            else: print("\n❌ Batch not found.")

        elif choice == '5':
            print("Closing portal..."); break

if __name__ == "__main__":
    run_portal()
