import requests
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

# Load login credentials
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

# Load pages
base_url = os.getenv("BASE_URL")
login_url = os.getenv("LOGIN_URL")
users_url = os.getenv("USERS_URL")
concerts_url = os.getenv("CONCERTS_URL")

# Load directories
data_base_path = os.getenv("DATA_BASE_PATH")
data_concerts_path = os.getenv("DATA_CONCERTS_PATH")

# Delete all files in the 'data/' directory
data_directory = Path(data_concerts_path)
for file in data_directory.iterdir():
    if file.is_file():
        file.unlink()

# Initialize session
with requests.Session() as session:
    # Get login page (may be needed for CSRF tokens)
    response = session.get(login_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find hidden tokens (if any used)
    hidden_inputs = soup.find_all("input", type="hidden")
    form_data = {input_tag["name"]: input_tag["value"] for input_tag in hidden_inputs if "name" in input_tag.attrs}

    # Add username and passowrd to form data
    form_data["username"] = username
    form_data["password"] = password

    # Login
    login_response = session.post(login_url, data=form_data)
    if login_response.status_code == 200:
        print("Logged succesfully")
        # Move to page Propozycje koncertów
        concerts_response = session.get(concerts_url)

        soup = BeautifulSoup(concerts_response.text, 'html.parser')
        concerts = soup.find_all(lambda tag: tag.name == 'span' and 'Ankieta:' in tag.text)

        # Get concert names with their links
        links = {}
        for concert in concerts:
            anchor = concert.find("a")
            if anchor.has_attr('href'):
                links[anchor.text.strip()] = base_url + anchor['href']

        number_of_concerts = len(links)
        print(f"Found {number_of_concerts} upcoming concerts.")

        # Iterate over each link and access the page
        for index, (concert_name, concert_url) in enumerate(links.items(), start=1):
            # Calculate and display progress
            progress = (index / number_of_concerts) * 100
            print(f"Progress {progress:.2f}%, Concert: {index}/{number_of_concerts}")
            try:
                # Get response from concert_url page
                response = session.get(concert_url)
                if response.status_code == 200:
                    page_soup = BeautifulSoup(response.text, "html.parser")
                    # Find the "Wyniki ankiety" link
                    show_results_link = page_soup.find('a', string="Wyniki ankiety")
                    if show_results_link:
                        poll_link = base_url + show_results_link['href']
                        try:
                            poll_response = session.get(poll_link)
                            if poll_response.status_code == 200:
                                results_soup = BeautifulSoup(poll_response.text, 'html.parser')
                                can_play_users = [a.text for a in results_soup.select('tr:nth-of-type(2) td:nth-of-type(2) a')]
                                cannot_play_users = [a.text for a in results_soup.select('tr:nth-of-type(3) td:nth-of-type(2) a')]
                                with open(f"{data_concerts_path}/{concert_name}", "w", encoding="utf-8") as file:
                                    for user in can_play_users:
                                        file.write(f"{user}\n")
                            else:
                                print(f"Failed to access poll results page: {poll_link}, Status Code: {poll_response.status_code}")
                        except requests.exceptions.RequestException as e:
                            print(f"Error accessing poll results page: {poll_link}: {e}")
                    else:
                        print(f"No poll results link found on page: {concert_url}")
                else:
                    print(f"Failed to access {concert_name}: {concert_url}, Status Code: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"Error accessing {concert_url}: {e}")
    else:
        "Login failed"


        



