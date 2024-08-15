import firebase_admin
from firebase_admin import credentials, db
import os
import json
onedrive_dir = os.path.join(os.path.expanduser("~"), "OneDrive")

# Path to the service account key JSON file
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
existing_data = ref.get()

# Determine the new product ID based on the number of existing products
if existing_data:
    new_product_id = len(existing_data)
else:
    new_product_id = "0"
print(new_product_id)

# Prompt for new product details
name_of_product = input("Enter the name of the product: ")
phone_number = input("Enter the phone number: ")
email = input("Enter the email: ")
# Prepare the new product data
new_product_data = {
    "product_name": name_of_product,
    "phone_number": phone_number if phone_number else defaultNumber,
    "email": email,
    "shipping_status": "to ship",
    "track_number": "",
    "location": "",
    "delivered": ""
}
if email:
    # Add the new product data to the database
    ref.child(new_product_id).set(new_product_data)

    print(f"Product {new_product_id} added successfully!")
