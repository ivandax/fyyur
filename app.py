#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#


import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import collections
import collections.abc
collections.Callable = collections.abc.Callable
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
# Imports config vars from config file
app.config.from_object('config')
db = SQLAlchemy(app)
# Add migration config
migrate = Migrate(app, db)

from models import Venue, Artist, Show

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


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

#  Create Venue
#  ----------------------------------------------------------------


@ app.route('/venues/create', methods=['GET'])
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


@ app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    try:
        form = VenueForm()
        name = form.name.data
        city = form.city.data
        state = form.state.data
        address = form.address.data
        phone = form.phone.data
        image_link = form.image_link.data
        facebook_link = form.facebook_link.data
        website_link = form.website_link.data
        seeking_talent = form.seeking_talent.data
        seeking_description = form.seeking_description.data
        genres = form.genres.data
        venue = Venue(name=name, state=state, city=city, address=address, phone=phone, image_link=image_link, facebook_link=facebook_link,
                      website_link=website_link, seeking_talent=seeking_talent, seeking_description=seeking_description, genres=genres)
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')
        print(sys.exc_info())
    finally:
        db.session.close()
    return render_template('pages/home.html')

def getUpcomingShows(shows):
    result = []
    for show in shows:
        if show.start_time > datetime.now(): 
            result.append(show.start_time)
    return result

@ app.route('/venues')
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

@ app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    result = Venue.query.filter(Venue.name.ilike(f'%{search_term}%'))

    response={
        "count": result.count(),
        "data": result
    }
    return render_template('pages/search_venues.html', results=response, search_term=search_term)

@ app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    try:
        venue = db.session.query(Venue).get(venue_id)
        data = createVenueResponse(venue)
        upcomingShowsQuery = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).all()
        pastShowsQuery = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).all()
        upcomingShows = []
        pastShows = []
        for show in upcomingShowsQuery:
            dict = {
                "artist_id": show.artist.id, 
                "artist_name": show.artist.name, 
                "artist_image_link": show.artist.image_link, 
                "start_time": format_datetime(str(show.start_time))
            }
            print(dict)
            upcomingShows.append(dict)
        for show in pastShowsQuery:
            dict = {
                "artist_id": show.artist.id, 
                "artist_name": show.artist.name, 
                "artist_image_link": show.artist.image_link, 
                "start_time": format_datetime(str(show.start_time))
            }
            pastShows.append(dict)
        data["upcoming_shows"] = upcomingShows
        data["past_shows"] = pastShows
        data["upcoming_shows_count"] = len(upcomingShows)
        data["past_shows_count"] = len(pastShows)
    except:
        print(sys.exc_info())    
    return render_template('pages/show_venue.html', venue=data)


@ app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return None

#  Update
#  --------------------------------------------------------------



@ app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    try: 
        query = db.session.query(Venue).get(venue_id)
        venue = createVenueResponse(query)
    except:
        print(sys.exc_info())
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@ app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    try:
        form = VenueForm()
        venue = Venue.query.get(venue_id)
        name = form.name.data
        venue.name = name
        venue.genres = form.genres.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.address = form.address.data
        venue.phone = form.phone.data
        venue.facebook_link = form.facebook_link.data
        venue.website_link = form.website_link.data
        venue.image_link = form.image_link.data
        venue.seeking_talent = form.seeking_talent.data
        venue.seeking_description = form.seeking_description.data
        db.session.commit()
        flash('Venue ' + name + ' has been updated')
    except:
        db.session.rollback()
        flash('An error occured while trying to edit Venue')
        print(sys.exc_info())
    finally:
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))

@ app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

def createArtistsResponse(artist):
    body = {}
    body['id'] = artist.id
    body['name'] = artist.name
    body['city'] = artist.city
    body['state'] = artist.state
    body['phone'] = artist.phone
    body['genres'] = artist.genres
    body['image_link'] = artist.image_link
    body['facebook_link'] = artist.facebook_link
    body['website_link'] = artist.website_link
    body['seeking_venue'] = artist.seeking_venue
    body['seeking_description'] = artist.seeking_description
    return body


@ app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:
    form = ArtistForm()
    name = form.name.data
    city = form.city.data
    state = form.state.data
    phone = form.phone.data
    image_link = form.image_link.data
    facebook_link = form.facebook_link.data
    website_link = form.website_link.data
    seeking_venue = form.seeking_venue.data
    seeking_description = form.seeking_description.data
    genres = form.genres.data
    artist = Artist(name=name, state=state, city=city, phone=phone, image_link=image_link, facebook_link=facebook_link,
                  website_link=website_link, seeking_venue=seeking_venue, seeking_description=seeking_description, genres=genres)
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully added!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------


@ app.route('/artists')
def artists():
    try:
        data = []
        artists = db.session.query(Artist).all()
        for artist in artists:
            result = {"id": artist.id, "name": artist.name}
            data.append(result)
        print(data)  
    except:
        print(sys.exc_info)
    return render_template('pages/artists.html', artists=data)


@ app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    result = Artist.query.filter(Artist.name.ilike(f'%{search_term}%'))
    response={
        "count": result.count(),
        "data": result
    }
    return render_template('pages/search_artists.html', results=response, search_term=search_term)


@ app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    try:
        artist = db.session.query(Artist).get(artist_id)
        data = createArtistsResponse(artist)
        upcomingShowsQuery = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
        pastShowsQuery = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.now()).all()
        upcomingShows = []
        pastShows = []
        for show in upcomingShowsQuery:
            dict = {
                "venue_id": show.artist.id, 
                "venue_name": show.artist.name, 
                "venue_image_link": show.artist.image_link, 
                "start_time": format_datetime(str(show.start_time))
            }
            upcomingShows.append(dict)
        for show in pastShowsQuery:
            dict = {
                "venue_id": show.artist.id, 
                "venue_name": show.artist.name, 
                "venue_image_link": show.artist.image_link, 
                "start_time": format_datetime(str(show.start_time))
            }
            pastShows.append(dict)
        data["upcoming_shows"] = upcomingShows
        data["past_shows"] = pastShows
        data["upcoming_shows_count"] = len(upcomingShows)
        data["past_shows_count"] = len(pastShows)
    except:
        print(sys.exc_info())
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@ app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    try: 
        query = db.session.query(Artist).get(artist_id)
        artist = createArtistsResponse(query)
    except:
        print(sys.exc_info())
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@ app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    try:
        form = ArtistForm()
        artist = Artist.query.get(artist_id)
        name = form.name.data
        artist.name = name
        artist.genres = form.genres.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.facebook_link = form.facebook_link.data
        artist.website_link = form.website_link.data
        artist.image_link = form.image_link.data
        artist.seeking_venue = form.seeking_venue.data
        artist.seeking_description = form.seeking_description.data
        db.session.commit()
        flash('Artist ' + name + ' has been updated')
    except:
        db.session.rollback()
        flash('An error occured while trying to edit Artist')
        print(sys.exc_info())
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))

@ app.route('/')
def index():
    return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@ app.route('/shows')
def shows():
    try:
        shows = db.session.query(Show).all()
        data = []
        for show in shows:
            data.append({
                "venue_id": show.venue_id,
                "venue_name": show.venue.name,
                "artist_id": show.artist_id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": format_datetime(str(show.start_time))
                })
    except:
        print(sys.exc_info())
    return render_template('pages/shows.html', shows=data)


@ app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@ app.route('/shows/create', methods=['POST'])
def create_show_submission():
    try:
        form = request.form
        artist_id = form['artist_id']
        venue_id = form['venue_id']
        start_time = form['start_time']

        venue = Venue.query.get(venue_id)
        artist = Artist.query.get(artist_id)
        show = Show(venue_id=venue.id, artist_id=artist.id, start_time=start_time)
    
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
        print(venue)
    except:
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')
        print(sys.exc_info())
    finally:
        db.session.close()
    return render_template('pages/home.html')


@ app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@ app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
