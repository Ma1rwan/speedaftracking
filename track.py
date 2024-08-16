import os
import json
import time
import smtplib
from firebase_admin import credentials, db
import firebase_admin
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
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

sender = mailConfig.get("sender")
receiver = mailConfig.get("receiver")
app_specific_password = mailConfig.get("app_specific_password")



# Query products that meet the criteria
query_results = ref.get()
PI_in_transit = []
TN_in_transit = []
locations = []
PN_in_transit = []


def send_email(product, status):
    # Remove specified characters from the string
    characters_to_remove = '【】'
    cleaned_string = ''.join(char for char in status if char not in characters_to_remove)

    # If you need to encode back to bytes, otherwise this step might be unnecessary
    descriptions = [f"{product} is {cleaned_string}"]
    result = "\n".join(descriptions)



    subject = "TRACKING BOT"
    message = result

    text = f"Subject: {subject}\n\n{message}"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    server.login(sender, app_specific_password)

    server.sendmail(sender, receiver, text)

    print("email has been sent")

def update_current_location(product_id, new_location, status):
    product_id = str(product_id)
    try:

        # Update only the 'current_location' field
        ref.child(product_id).update({"location": new_location})
        if status == "Delivered":
            ref.child(product_id).update({"delivered": True})
            print(product_id)
    except Exception as e:
        print(f"Error updating current location for product {product_id}: {e}")
if query_results:
    product_ID = 0
    for result in query_results:
        if result.get('delivered', '') == False:
            PI_in_transit.append(product_ID)
            TN_in_transit.append(result.get('track_number', ''))
            locations.append(result.get('location', ''))
            PN_in_transit.append(result.get('product_name', ''))
            print(result.get('location', ''))

        product_ID += 1

else:
    print("No products found that meet the criteria.")
print(PN_in_transit)
print(PN_in_transit)





path = onedrive_dir + r"\Documents\coding\python\driver\geckodriver.exe"

products_names = []
products_prices = []
# Create Firefox options
url = "https://www.speedaf.com/ma-en"
firefox_options = webdriver.FirefoxOptions()
firefox_options.add_argument("--headless")
# Set the path to the Firefox executable (optional, you can omit this line if Firefox is in your system PATH)
firefox_options.binary_location = "D:\\Program Files\\Mozilla Firefox\\firefox.exe"  # Adjust the path accordingly

# Create a Firefox WebDriver instance with options
driver = webdriver.Firefox(options=firefox_options)

# Open the URL
try:
    for index, productID in enumerate(PI_in_transit):
        driver.get(url)
        input = driver.find_element(By.XPATH,
                                    '/html/body/div/div/div/main/div[2]/div/div/div[1]/div/div/div/div/input')
        input.click()
        time.sleep(1)
        input = driver.find_element(By.XPATH, '//*[@id="waybillInput"]')
        input.send_keys(TN_in_transit[index])
        time.sleep(1)
        trackbut = driver.find_element(By.XPATH,
                                       '/html/body/div/div/div/main/div[2]/div/div/div[1]/div/div/div[2]/div[1]/button/span')
        trackbut.click()
        time.sleep(3)
        html_source = driver.page_source
        soup = BeautifulSoup(html_source, "html.parser")
        element = soup.find(class_="track-infomation")
        if element:
            element = element.text
            # Remove specified characters from the string
            characters_to_remove = '【】'
            check_element = ''.join(char for char in element if char not in characters_to_remove)
            print(element)
            if "Parcel delivered" in check_element:
                update_current_location(productID, element, "Delivered")
                send_email(PN_in_transit[index], element)
            elif element != locations[index]:
                # List of keywords to check for
                keywords = ["DC-CASA", "Marrakech", "scanned for delivery", "Issue Parcel"]

                check_element2 = check_element.lower()
                for keyword in keywords:
                    if keyword.lower() in check_element2:
                        update_current_location(productID, element, "shipped")
                        send_email(PN_in_transit[index], element)
                        break  # Stop further checks once a keyword is found

            time.sleep(5)  # Sleep for 10 seconds, adjust as needed
    driver.quit()
except Exception as e:
    print(e)
    driver.quit()