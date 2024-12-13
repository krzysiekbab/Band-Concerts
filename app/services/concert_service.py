from .. import db
from app.models import Concert, Musician
from datetime import datetime
import json
from typing import List, Dict
from flask import Flask
from app import get_project_base_path
import os

def add_concerts_to_database(app: Flask) -> None:
    """
    Add concerts to the database
    """
    with app.app_context():
        concerts_data = load_concerts_data()
        for _, concert in concerts_data.items():
            add_concert_to_database(concert)

def add_concert_to_database(concert_data: Dict) -> None:
    """
    Add concert to database
    """
    if concert_exists_in_database(concert_data['id']) == False:
        concert = Concert(
            id=concert_data['id'],
            name=concert_data['name'],
            shortname=concert_data['shortname'],
            date=datetime.strptime(concert_data['date'], "%Y.%m.%d"),
        )
        add_musicians_to_concert(concert_data, concert)

        db.session.add(concert)
        db.session.commit()

        print(f"{concert_data['name']} added to database")

def remove_concert_from_database(concert: Concert) -> None:
    """
    Remove concert from database
    """
    concert_name = concert.name
    db.session.remove(concert)
    db.session.commit()

    print(f"{concert_name} removed from database")

def add_musicians_to_concert(concert_data: Dict, concert: Concert) -> None:
    """
    Add musicians to concert
    """
    for musician_nick in concert_data['can_play_users']:
        musician = Musician.query.filter_by(nick=musician_nick).first()
        if is_musician_already_added_to_concert(musician, concert) == False:
            add_musician_to_concert(musician, concert)

def add_musician_to_concert(musician: Musician, concert: Concert) -> None:
    """
    Add a musician to a concert.
    """
    concert.musicians.append(musician)
    db.session.commit()
    print(f"{musician.get_fullname()} added to concert {concert.name}.")

def remove_musician_from_concert(musician: Musician, concert: Concert) -> None:
    """
    Remove a musician from a concert if they are associated.
    """
    concert.musicians.remove(musician)
    db.session.commit()
    print(f"{musician.get_fullname()} has been removed from the concert {concert.name}.")

def is_musician_already_added_to_concert(musician: Musician, concert: Concert) -> bool:
    """
    Check if musician already added to concert musicians
    """
    return musician in concert.musicians

def concert_exists_in_database(concert_id: int) -> bool:
    """
    Check if a concert with the given ID exists in the database.
    """
    return Concert.query.filter_by(id=concert_id).first() is not None

def update_concert_database() -> None:
    """
    Update concert database based on scrapped concerts data
    """
    from run import app
    concerts_data = load_concerts_data()

    with app.app_context():
        # Remove concerts, which not present anymore in scrapped concerts data
        concerts: List[Concert] = Concert.query.all()
        for concert in concerts:
            if str(concert.id) not in concerts_data.keys():
                remove_concert_from_database(concert)
        
        # Update info about upcoming concerts
        for _, concert_data in concerts_data.items():
            concert_exists = concert_exists_in_database(concert_data['id'])
            if concert_exists == False:
                add_concert_to_database(concert_data)
            else:
                concert = Concert.query.filter_by(id=concert_data['id']).first()
                update_musicians_in_concert(concert_data, concert)


def update_musicians_in_concert(concert_data: Dict, concert: Concert) -> None:
    """
    Update musicians participating in a concert
    """
    musicians: List[Musician] = concert.musicians
    
    # Remove musicians, who are not participating anymore in a concert
    for musician in musicians:
        if musician.nick not in concert_data['can_play_users']:
            remove_musician_from_concert(musician, concert)
    
    # Update info about musicians participating in concert
    add_musicians_to_concert(concert_data, concert)
     

def load_concerts_data() -> Dict:
    """
    Load scrapped concert data
    """
    concerts_file_path = os.path.join(get_project_base_path(), 'data', 'concerts.json')
    with open(concerts_file_path, 'r', encoding='utf-8') as file:
        concerts_data = json.load(file)

        return concerts_data
    
def get_concerts_modified_time():
    """
    Get the last modified time of a concerts.json.

    Returns:
        str: Last modified time in 'YYYY-MM-DD HH:MM:SS' format, or an error message.
    """
    concerts_file_path = os.path.join(get_project_base_path(), 'data', 'concerts.json')

    try:
        if os.path.exists(concerts_file_path):
            modified_time = os.path.getmtime(concerts_file_path)
            readable_time = datetime.fromtimestamp(modified_time).strftime('%Y-%m-%d %H:%M')
            
            return readable_time
        else:
            return f"The file {concerts_file_path} does not exist."
    except Exception as e:
        return f"An error occurred: {e}"
