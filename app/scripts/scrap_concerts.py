import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import re
import json
from app import database_exists
from app.services.concert_service import update_concert_database
from app import logger

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

def scrap_concerts():
    # Initialize session
    with requests.Session() as session:
        logger.info("Scraping concerts started...")
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
            logger.info("Logged succesfully")
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
            logger.info(f"Found {number_of_concerts} upcoming concerts. Starting gathering info about each of them...")
            concert_data = {}
            
            # Iterate over each link and access the page
            for index, (concert_name, concert_url) in enumerate(links.items(), start=1):
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

                                    # Regular expression to match the id from url
                                    match_id = re.search(r"tid=(\d+)", concert_url)
                                    concert_id = match_id.group(1)

                                    # Regular expression to match the date format
                                    match = re.match(r"^(\d{4}\.\d{2}\.\d{2})\s(.+)$", concert_name)
                                    concert_date = match.group(1)
                                    short_name = match.group(2)
                                    concert_data[str(concert_id)] = {
                                        'id': int(concert_id),
                                        'name': concert_name,
                                        'shortname': short_name,
                                        'date': concert_date,
                                        'can_play_users': can_play_users,
                                        'cannot_play_users': cannot_play_users,
                                        'url': concert_url
                                    }
                                    # Calculate and display progress
                                    progress = (index / number_of_concerts) * 100
                                    logger.info(f"Progress {progress:.2f}%, Gathered: {index}/{number_of_concerts} concerts")
                                else:
                                    logger.error(f"Failed to access poll results page: {poll_link}, Status Code: {poll_response.status_code}")
                            except requests.exceptions.RequestException as e:
                                logger.error(f"Error accessing poll results page: {poll_link}: {e}")
                        else:
                            logger.error(f"No poll results link found on page: {concert_url}")
                    else:
                        logger.error(f"Failed to access {concert_name}: {concert_url}, Status Code: {response.status_code}")
                except requests.exceptions.RequestException as e:
                    logger.error(f"Error accessing {concert_url}: {e}")

            logger.info("Gathering concert data finished.")

            # Save data into .json file
            with open(f"{data_base_path}/concerts.json", "w", encoding="utf-8") as file:
                json.dump(concert_data, file, indent=4, ensure_ascii=False)
        else:
            logger.error("Login failed.")

if __name__ == "__main__":
    scrap_concerts()
    if database_exists():
        update_concert_database()
    else:
        logger.error(f"Database file is missing! Cannot update database")

        



