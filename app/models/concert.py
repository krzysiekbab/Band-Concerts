from .. import db
from .associations import db, concert_musician_association
from sqlalchemy.orm import relationship

class Concert(db.Model):
    __tablename__ = 'concerts'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    shortname = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime(timezone=True), nullable=False)
    url = db.Column(db.String(100), nullable=False)

    # Define the many-to-many relationship with Musician
    musicians = relationship('Musician', secondary=concert_musician_association, back_populates='concerts')

