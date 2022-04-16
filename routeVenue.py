from app import db

from forms import *
from flask import Blueprint, render_template, request, Response, flash, redirect, url_for

from models import Venue
import sys

venueRoute = Blueprint('venueRoute', __name__)

#  Create Venue
#  ----------------------------------------------------------------


@venueRoute.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


def createVenueResponse(venue):
    body = {}
    body['name'] = venue.name
    body['city'] = venue.city
    body['state'] = venue.state
    body['address'] = venue.address
    body['phone'] = venue.phone
    body['image_link'] = venue.image_link
    body['facebook_link'] = venue.facebook_link
    body['website_link'] = venue.website_link
    body['seeking_talent'] = venue.seeking_talent
    body['seeking_description'] = venue.seeking_description
    body['genres'] = venue.genres
    return body


@venueRoute.route('/venues/create', methods=['POST'])
def create_venue_submission():
    try:
        form = request.form
        name = form['name']
        city = form['city']
        state = form['state']
        address = form['address']
        phone = form['phone']
        image_link = form['image_link']
        facebook_link = form['facebook_link']
        website_link = form['website_link']
        seeking_talent = True if form.get(
            'seeking_talent', False) == 'y' else False
        seeking_description = form['seeking_description']
        genres = form['genres']
        print(genres, type(genres), type(seeking_talent))
        venue = Venue(name=name, state=state, city=city, address=address, phone=phone, image_link=image_link, facebook_link=facebook_link,
                      website_link=website_link, seeking_talent=seeking_talent, seeking_description=seeking_description, genres=[genres])
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
        data = createVenueResponse(venue)
        print(data)
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')
        print(sys.exc_info)
    finally:
        db.session.close()
    return render_template('pages/home.html')