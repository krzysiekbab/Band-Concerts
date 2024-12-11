from .. import db
from .associations import db, concert_musician_association
from sqlalchemy.orm import relationship

class Concert(db.Model):
    __tablename__ = 'concerts'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    shortname = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime(timezone=True), nullable=False)

    # Define the many-to-many relationship with Musician
    musicians = relationship('Musician', secondary=concert_musician_association, back_populates='concerts')

    def remove_musician(self, musician):
        """Remove a musician from the concert."""
        if musician in self.musicians:
            self.musicians.remove(musician)
        else:
            raise ValueError(f"Musician {musician.name} {musician.surname} is not part of this concert.")



