from .. import db

concert_musician_association = db.Table(
    'concert_musician_association',
    db.Column('concert_id', db.Integer, db.ForeignKey('concerts.id'), primary_key=True),
    db.Column('musician_id', db.Integer, db.ForeignKey('musicians.id'), primary_key=True)
)