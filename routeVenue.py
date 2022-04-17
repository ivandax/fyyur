from app import db

from forms import *
from flask import Blueprint, render_template, request, Response, flash, redirect, url_for
from sqlalchemy.orm import lazyload
from datetime import datetime
import dateutil.parser
import babel

from models import Venue, Artist
import sys
import json

venueRoute = Blueprint('venueRoute', __name__)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    if isinstance(value, str):
        date = dateutil.parser.parse(value)
    else: 
        date = value
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')

#  Create Venue
#  ----------------------------------------------------------------


@venueRoute.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


def createVenueResponse(venue):
    body = {}
    body['id'] = venue.id
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
        venue = Venue(name=name, state=state, city=city, address=address, phone=phone, image_link=image_link, facebook_link=facebook_link,
                      website_link=website_link, seeking_talent=seeking_talent, seeking_description=seeking_description, genres=[genres])
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
        data = createVenueResponse(venue)
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')
        print(sys.exc_info)
    finally:
        db.session.close()
    return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------

def getUpcomingShows(shows):
    result = []
    for show in shows:
        if show.start_time > datetime.now(): 
            result.append(show.start_time)
    return result

@venueRoute.route('/venues')
def venues():
    try:
        venuesMap = {}
        venues = db.session.query(Venue).all()
        for venue in venues:
            key = venue.city+venue.state
            upcomingShows = getUpcomingShows(venue.artists)
            numUpcomingShows = len(upcomingShows)
            newVenue = {"id": venue.id, "name": venue.name, "num_upcoming_shows": numUpcomingShows }
            if key in venuesMap:
                currentVenues = venuesMap[key]["venues"]
                currentVenues.append(newVenue)
                venuesMap[key]["venues"] = currentVenues
            else:
                venuesMap[key] = {
                    "city": venue.city,
                    "state": venue.state,
                    "venues": [newVenue]
                    }
        data = list(venuesMap.values())
        print(data)  
    except:
        print(sys.exc_info)

    return render_template('pages/venues.html', areas=data)

@venueRoute.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    response = {
        "count": 1,
        "data": [{
            "id": 2,
            "name": "The Dueling Pianos Bar",
            "num_upcoming_shows": 0,
        }]
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@venueRoute.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    try:
        venue = db.session.query(Venue).get(venue_id)
        shows = venue.artists
        data = createVenueResponse(venue)
        upcomingShows = []
        pastShows = []
        for show in shows:
            artist = show.artist
            artistDict = {
                "artist_id": artist.id, 
                "artist_name": artist.name, 
                "artist_image_link": artist.image_link, 
                "start_time": format_datetime(str(show.start_time))
            }
            if show.start_time > datetime.now():
                upcomingShows.append(artistDict)
            else:
                pastShows.append(artistDict)
        data["upcoming_shows"] = upcomingShows
        data["past_shows"] = pastShows
        data["upcoming_shows_count"] = len(upcomingShows)
        data["past_shows_count"] = len(pastShows)
    except:
        print(sys.exc_info())    
    return render_template('pages/show_venue.html', venue=data)


@venueRoute.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Update
#  --------------------------------------------------------------



@venueRoute.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = {
        "id": 1,
        "name": "The Musical Hop",
        "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
        "address": "1015 Folsom Street",
        "city": "San Francisco",
        "state": "CA",
        "phone": "123-123-1234",
        "website": "https://www.themusicalhop.com",
        "facebook_link": "https://www.facebook.com/TheMusicalHop",
        "seeking_talent": True,
        "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
        "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    }
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@venueRoute.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    return redirect(url_for('show_venue', venue_id=venue_id))