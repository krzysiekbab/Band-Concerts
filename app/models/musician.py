from .. import db
from .associations import db, concert_musician_association
from sqlalchemy.orm import relationship

class Musician(db.Model):
    __tablename__ = 'musicians'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    nick = db.Column(db.String(100), unique=True, nullable=False)
    instrument = db.Column(db.String(100), nullable=True)

    # Define the many-to-many relationship with Concert
    concerts = relationship('Concert', secondary=concert_musician_association, back_populates='musicians')

    def get_fullname(self):
        return f'{self.name} {self.surname}'
    
    def __repr__(self):
        return f'<User {self.name} {self.surname}, {self.nick}, {self.instrument}>' 