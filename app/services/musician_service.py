from .. import db
from app.models import Musician
from typing import List, Dict
from flask import Flask
import json
from app import get_project_base_path, logger
import os

def add_musicians_to_database(app: Flask) -> None:
    """
    Add forum musicians to database
    """
    with app.app_context():
        musicians_data = load_musicians_data()
        for _, musician in musicians_data.items():
            add_musician_to_database(musician)

def add_musician_to_database(musician_data: Dict) -> None:
    """
    Add musician to database
    """
    if musician_exists_in_database(musician_data['id']) == False:
        musician = Musician(
            id=musician_data['id'],
            name=musician_data['name'],
            surname=musician_data['surname'],
            nick=musician_data['nick'],
            instrument=musician_data.get('instrument')
        )
        db.session.add(musician)
        db.session.commit()
        
        logger.info(f"{musician.get_fullname()} added to database")

def remove_musician_from_database(musician: Musician) -> None:
    """
    Remove musician from database
    """
    full_name = musician.get_fullname()
    db.session.delete(musician)
    db.session.commit()

    logger.info(f"{full_name} removed from database")

def update_musician_database() -> None:
    """
    Update musician database based on scrapped musicians data
    """
    from run import app

    musicians_data = load_musicians_data()
    with app.app_context():
        # Remove musician, who is not present anymore in scrapepd musicians data
        musicians: List[Musician] = Musician.query.all()
        for musician in musicians:
            if str(musician.id) not in musicians_data.keys():
                remove_musician_from_database(musician)

        # Add new musicians
        for _, musician in musicians_data.items():
            if musician_exists_in_database(musician['id']) == False:
                add_musician_to_database(musician)


def musician_exists_in_database(musician_id: int) -> bool:
    """
    Check if a musician with the given ID exists in the database.
    """
    return Musician.query.filter_by(id=musician_id).first() is not None

def divide_musicians_into_instrument_sections(musicians: List[Musician]) -> Dict:
    """
    Divide musicians into instrument sections to have them easy displayed on concert page
    """
    sections = {}
    for musician in musicians:
        instrument = musician.instrument
        if instrument in sections:
            sections[instrument].append(musician)
        elif instrument == None:
            sections["Inne"] = [musician]
        else:
            sections[instrument] = [musician]
    
    return sections

def load_musicians_data() -> Dict:
    """
    Load scrapped musician data
    """
    musicians_file_path = os.path.join(get_project_base_path(), 'data', 'musicians.json')
    with open(musicians_file_path, 'r', encoding='utf-8') as file:
        musicians_data = json.load(file)

        return musicians_data
    