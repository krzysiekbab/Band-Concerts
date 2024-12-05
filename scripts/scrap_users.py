import requests
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
import csv


load_dotenv()

# Load login credentials
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

# Load pages
login_url = os.getenv("LOGIN_URL")
users_url = os.getenv("USERS_URL")

# Load file paths for users data
data_base_path = os.getenv("DATA_BASE_PATH")
active_musicians_path = os.getenv("ACTIVE_MUSICIANS_PATH")

data_dict = {}

# Open and read the CSV file
with open(active_musicians_path, mode='r', encoding='utf-8-sig') as file:
    reader = csv.reader(file, delimiter=';')
    for row in reader:
        if len(row) == 3:
            key = f"{row[1]} {row[2]}"
            value = row[0]
            data_dict[key] = value

# Initialize session
with requests.Session() as session:
    # Get login page (may be needed for CSRF tokens)
    response = session.get(login_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find hidden tokens(if any used)
    hidden_inputs = soup.find_all("input", type="hidden")
    form_data = {input_tag["name"]: input_tag["value"] for input_tag in hidden_inputs if "name" in input_tag.attrs}

    # Add username and passowrd to form data
    form_data["username"] = username
    form_data["password"] = password

    # Login
    login_response = session.post(login_url, data=form_data)
    if "Logowanie nieudane" in login_response.text:
        print("Nie udało się zalogować.")
    else:
        print("Zalogowano pomyślnie.")

        # Move to users page
        users_response = session.get(users_url)

        # Gather all links with "uid=" in href
        soup = BeautifulSoup(users_response.text, 'html.parser')
        links = soup.find_all("a", href=True)
        user_links = [link['href'] for link in links if 'uid=' in link['href']]

        print(f"Found {len(user_links)} users. Starting gathering info about each of them...")

        users_data = []

        for index, user_link in enumerate(user_links):
            user_response = session.get(user_link)
            user_soup = BeautifulSoup(user_response.text, 'html.parser')

            # Gather user data
            user_id = user_link.split('uid=')[1]
            imie = user_soup.find("td", class_="trow1 scaleimages")
            nazwisko = user_soup.find("td", class_="trow2 scaleimages")
            nick_container = user_soup.find('span', class_='largetext').find('strong')
            nick = nick_container.find('span') if nick_container else None

            if not nick:
                nick = nick_container

            if user_id and imie and nazwisko and nick:
                name = imie.get_text(strip=True)
                surname = nazwisko.get_text(strip=True)
                nick = nick.get_text(strip=True)
                full_name = f"{surname} {name}"
                instrument = data_dict.get(full_name)

                user_data = {
                    'id': user_id,
                    'name': name,
                    'surname': surname,
                    'nick': nick,
                    'instrument': instrument
                }
                users_data.append(user_data)

            progress = (index + 1) / len(user_links) * 100
            print(f"Progress: {progress:.2f}% - Gathered {index + 1}/{len(user_links)} users", end='\r')

        print("\nGathering data finished.")

        # Save data into .txt file
        filename = f"{data_base_path}/scrapped_users.txt"
        with open(f"{filename}", "w", encoding="utf-8") as file:
            for user in users_data:
                file.write(f"'{user['nick']}': {{'id': {user['id']}, 'name': '{user['name']}', 'surname': '{user['surname']}', 'instrument': '{user['instrument']}'}}\n")
        
        print(f"Saved users data to {filename}")


        
