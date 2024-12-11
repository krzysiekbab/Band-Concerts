from .. import db
from app.models import Concert, Musician
from datetime import datetime

def add_concert_to_database(concert_data):
    existing_concert = Concert.query.filter_by(id=concert_data['id']).first()
    if existing_concert is None:
        new_concert = Concert(
            id=concert_data['id'],
            name=concert_data['name'],
            shortname=concert_data['shortname'],
            date=datetime.strptime(concert_data['date'], "%Y.%m.%d"),
        )
        
        # TODO: use some different method
        for musician_nick in concert_data['can_play_users']:
            musician = Musician.query.filter_by(nick=musician_nick).first()
            new_concert.musicians.append(musician)
        db.session.add(new_concert)
        db.session.commit()

        print(f"{concert_data['name']} added to database")

# Add musician to concert only if not already associated
def add_musician_to_concert(concert: Concert, musician: Musician) -> None:
    """
    Adds a musician to a concert only if the musician is not already associated with it.
    """
    if musician in concert.musicians:
        print(f"Musician {musician.name} is already associated with the concert {concert.name}.")
        return
    
    concert.musicians.append(musician)
    db.session.commit()
    print(f"Musician {musician.name} successfully added to concert {concert.name}.")