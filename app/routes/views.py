from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Musician, Concert
from typing import List
from app.services.musician_service import divide_musicians_into_instrument_sections

views = Blueprint("views", __name__)

@views.route("/")
@views.route("/home")
@login_required
def home():
    musicians = Musician.query.all()
    concerts = Concert.query.order_by(Concert.date.asc()).all()
    
    return render_template("home.jinja", user=current_user, musicians=musicians, concerts=concerts)


@views.route("/concerts/<id>")
@login_required
def show_concert(id: int):
    concert = Concert.query.filter_by(id=id).first()
    musicians: List[Musician] = concert.musicians
    sections = divide_musicians_into_instrument_sections(musicians)
    
    return render_template("concert.jinja", user=current_user, concert=concert, musicians=musicians, sections=sections)

