from .. import db
from app.models import Musician
from typing import List, Dict


def add_musician_to_database(user_data):
    """
    Add musician to database only if not added already
    """
    from app.models import Musician
    existing_musician = Musician.query.filter_by(id=user_data['id']).first()
    if existing_musician is None:
        new_musician = Musician(
            id=user_data['id'],
            name=user_data['name'],
            surname=user_data['surname'],
            nick=user_data['nick'],
            instrument=user_data.get('instrument')
        )
        db.session.add(new_musician)
        db.session.commit()
        print(f"{user_data['name']} {user_data['surname']} added to database")

def divide_musicians_into_instrument_sections(musicians: List[Musician]) -> Dict:
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