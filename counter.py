import firebase_admin
from firebase_admin import credentials, db
import os
import json
onedrive_dir = os.path.join(os.path.expanduser("~"), "OneDrive")

# Path to the service account key JSON file
# Load configuration files
with open(os.path.join(onedrive_dir, 'Documents/coding/data/trackingDB/config.json')) as DBconfig_file:
    DBconfig = json.load(DBconfig_file)

with open(os.path.join(onedrive_dir, 'Documents/coding/data/sendmail/config.json')) as mailConfig_file:
    mailConfig = json.load(mailConfig_file)

cred = credentials.Certificate(os.path.join(onedrive_dir, 'Documents/coding/data/trackingDB/db-firebase-adminsdk.json'))
# Initialize the Firebase app with the database URL from the config file
firebase_admin.initialize_app(cred, {
    'databaseURL': DBconfig['databaseURL']
})
# Initialize the Firebase app with the database URL from the config file

# Reference to your Firebase database
ref = db.reference('/tracking')
defaultNumber = mailConfig.get("defaultNumber")
# Get existing data
query_results = ref.get()

product_names = []
phone_numbers = []
track_numbers = []
locations = []
if query_results:
    in_transit = 0
    in_local_country = 0
    out_for_delivery = 0
    to_ship = 0
    closed = 0
    delivered_count = 0
    for result in query_results:
        if result.get('delivered', '') == False:
            if "in transit" in result.get('location', '') :
                in_transit += 1
            elif "DC-CASA" in result.get('location', '') or "Hub Marrakech" in result.get('location', ''):
                in_local_country += 1
            elif "scanned for delivery" in result.get('location', ''):
                out_for_delivery += 1
                product_names.append(result.get('product_name', ''))
                phone_numbers.append(result.get('phone_number', ''))
                track_numbers.append(result.get('track_number', ''))
                locations.append(result.get('location', ''))
        elif result.get('delivered', '') == True:
            delivered_count += 1
        else:
            if result.get('shipping_status', '') == "to ship":
                to_ship += 1
            else:
                closed += 1


    result_file = onedrive_dir + r"\سطح المكتب\transit.txt"
    with open(result_file, 'w', encoding='utf-8') as file:
        file.write(f"in transit: {in_transit}\n")
        file.write(f"In local country: {in_local_country}\n")
        file.write(f"Out for delivery: {out_for_delivery}\n")
        file.write(f"To ship: {to_ship}\n")
        file.write(f"Closed: {closed}\n")
        file.write(f"Delivered: {delivered_count}\n")

    output_file = onedrive_dir + r"\سطح المكتب\livreur.txt"
    with open(output_file, 'w', encoding='utf-8') as file2:
        if out_for_delivery > 0:
            for index, product_name in enumerate(product_names):

                last_index = locations[index].rfind("delivery courier is")
                if last_index != -1:
                    last_index = last_index + len("delivery courier is") + 1
                    file2.write(f"{product_name} | {phone_numbers[index]} | {track_numbers[index]} | {locations[index][last_index:].strip()}\n")
        else:
            file2.write("NOTHING HERE!!!!!!")