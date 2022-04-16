from app import db

from forms import *
from flask import Blueprint, render_template, request, Response, flash, redirect, url_for

from models import Artist
import sys

artistRoute = Blueprint('artistRoute', __name__)

#  Create Artist
#  ----------------------------------------------------------------


@artistRoute.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

def createArtistsResponse(artist):
    body = {}
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


@artistRoute.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:
    form = request.form
    name = form['name']
    city = form['city']
    state = form['state']
    phone = form['phone']
    image_link = form['image_link']
    facebook_link = form['facebook_link']
    website_link = form['website_link']
    seeking_venue = True if form.get(
        'seeking_venue', False) == 'y' else False
    seeking_description = form['seeking_description']
    genres = form['genres']
    artist = Artist(name=name, state=state, city=city, phone=phone, image_link=image_link, facebook_link=facebook_link,
                  website_link=website_link, seeking_venue=seeking_venue, seeking_description=seeking_description, genres=[genres])
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully added!')
    data = createArtistsResponse(artist)
    print(data)
  except:
    print("we enter here")
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------


@artistRoute.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = [{
        "id": 4,
        "name": "Guns N Petals",
    }, {
        "id": 5,
        "name": "Matt Quevedo",
    }, {
        "id": 6,
        "name": "The Wild Sax Band",
    }]
    return render_template('pages/artists.html', artists=data)


@artistRoute.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    response = {
        "count": 1,
        "data": [{
            "id": 4,
            "name": "Guns N Petals",
            "num_upcoming_shows": 0,
        }]
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@artistRoute.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    data1 = {
        "id": 4,
        "name": "Guns N Petals",
        "genres": ["Rock n Roll"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
        "past_shows": [{
            "venue_id": 1,
            "venue_name": "The Musical Hop",
            "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
            "start_time": "2019-05-21T21:30:00.000Z"
        }],
        "upcoming_shows": [],
        "past_shows_count": 1,
        "upcoming_shows_count": 0,
    }
    data2 = {
        "id": 5,
        "name": "Matt Quevedo",
        "genres": ["Jazz"],
        "city": "New York",
        "state": "NY",
        "phone": "300-400-5000",
        "facebook_link": "https://www.facebook.com/mattquevedo923251523",
        "seeking_venue": False,
        "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
        "past_shows": [{
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
            "start_time": "2019-06-15T23:00:00.000Z"
        }],
        "upcoming_shows": [],
        "past_shows_count": 1,
        "upcoming_shows_count": 0,
    }
    data3 = {
        "id": 6,
        "name": "The Wild Sax Band",
        "genres": ["Jazz", "Classical"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "432-325-5432",
        "seeking_venue": False,
        "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "past_shows": [],
        "upcoming_shows": [{
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
            "start_time": "2035-04-01T20:00:00.000Z"
        }, {
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
            "start_time": "2035-04-08T20:00:00.000Z"
        }, {
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
            "start_time": "2035-04-15T20:00:00.000Z"
        }],
        "past_shows_count": 0,
        "upcoming_shows_count": 3,
    }
    data = list(filter(lambda d: d['id'] ==
                       artist_id, [data1, data2, data3]))[0]
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@artistRoute.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = {
        "id": 4,
        "name": "Guns N Petals",
        "genres": ["Rock n Roll"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    }
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@artistRoute.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    return redirect(url_for('show_artist', artist_id=artist_id))



@artistRoute.route('/venues/<int:venue_id>/edit', methods=['GET'])
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


@artistRoute.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    return redirect(url_for('show_venue', venue_id=venue_id))