#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)
    shows = db.relationship('Show', backref='venue', lazy=True)


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String)
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)
    shows = db.relationship('Show', backref='artist', lazy=True)

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime) 


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  venue_query = Venue.query.all()
  data = []
  for venue in venue_query:
    data.append({
      "city": venue.city,
      "state": venue.state,
      "venues": [{
        "id": venue.id,
        "name": venue.name
      }]
    })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  search_result = Venue.query().filter(Venue.name.ilike(f'%{search_term}%')).all()
  data = []
  for hit in search_result:
    data.append({
      "id": hit.id,
      "name": hit.name,
      "num_upcoming_shows": len(Shows.query.join(Venue).filter(Show.venue_id==hit.id).filter(Show.start_time > datetime.now()).all())
    })

  response={
    "count": len(search_result),
    "data": data
  }
 
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  
  upcoming_shows_query = Show.query.join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time > datetime.now()).all()
  upcoming_shows = []
  for show in upcoming_shows_query:
    upcoming_shows.append({
    "artist_id": show.artist_id,
    "artist_name": show.artist_name,
    "artist_image_link": show.artist.image_link,
    "start_time": show.start_time
  })

  past_shows_query = Show.query.join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time < datetime.now()).all()
  past_shows = []
  for show in past_shows_query:
    past_shows.append({
    "artist_id": show.artist_id,
    "artist_name": show.artist_name,
    "artist_image_link": show.artist.image_link,
    "start_time": show.start_time
  })

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  try:
    # get all the data from the form
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    img_link = request.form.get('image_link')
    genres = request.form.get('genres')
    facebook_link = request.form.get('facebook_link')
    website = request.form.get('website')
    seeking_talent = request.form.get('seeking_talent')
    seeking_description = request.form.get('seeking_description')
    venue = Venue(name = name, city = city, state = state, address = address, phone = phone, image_link = img_link, genres = genres, facebook_link = facebook_link, website = website, seeking_talent = seeking_talent, seeking_description = seeking_description)
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    if error:
      flash('Venue was not created')
      db.session.close()
    else:
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
      db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue_to_be_deleted = Venue.query.get(venue_id)
    db.session.delete(venue_to_be_deleted)
    db.sesison.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return jsonify({ 'success': True })
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artist_query = Artist.query.all()
  data=[]
  for artist in artist_query:
    data.append({
      "id": artist.id,
      "name": artist.name
    })
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  search_result = Artist.query().filter(Artist.name.ilike(f'%{search_term}%')).all()
  data = []
  for hit in search_result:
    data.append({
      "id": hit.id,
      "name": hit.name,
      "num_upcoming_shows": len(Shows.query.join(Venue).filter(Show.artist_id==hit.id).filter(Show.start_time > datetime.now()).all())
    })

  response={
    "count": len(search_result),
    "data": data
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # TODO: replace with real venue data from the venues table, using venue_id
  artist = Artist.query.get(artist_id)
  
  upcoming_shows_query = Show.query.join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time > datetime.now()).all()
  upcoming_shows = []
  for show in upcoming_shows_query:
    upcoming_shows.append({
    "venue_id": show.venue_id,
    "venue_name": show.venue_name,
    "venue_image_link": show.venue.image_link,
    "start_time": show.start_time
  })

  past_shows_query = Show.query.join(Venue).filter(Show.venue_id==artist_id).filter(Show.start_time < datetime.now()).all()
  past_shows = []
  for show in past_shows_query:
    past_shows.append({
    "venue_id": show.venue_id,
    "venue_name": show.venue_name,
    "venue_image_link": show.venue.image_link,
    "start_time": show.start_time
  })

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }  


  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  form.name = artist.name
  form.city = artist.city
  form.state = artist.state
  form.phone = artist.phone
  form.image_link = artist.image_link
  form.genres = artist.genres
  form.facebook_link = artist.facebook_link
  form.website = artist.website
  form.seeking_venue = artist.seeking_venue
  form.seeking_description = artist.seeking_description

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  artist = Artist.query.get(venue_id)
  try:
    # GET all the data from the form
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.image_link = request.form.get('image_link')
    artist.genres = request.form.get('genres')
    artist.facebook_link = request.form.get('facebook_link')
    artist.website = request.form.get('website')
    artist.seeking_venue = request.form.get('seeking_venue')
    artist.seeking_description = request.form.get('seeking_description')
    artist.db.session.commit()
  except:
    error = False
    db.session.rollback()
  finally:
    if error == True:
      db.session.close()
      flash('Artist was successfully updated')
    else:
      db.session.close()
      flash('Artist was not successfully updated')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue.id)
  form.name = venue.name
  form.city = venue.city
  form.state = venue.state
  form.address = venue.address
  form.phone = venue.phone
  form.image_link = venue.image_link
  form.genres = venue.genres
  form.facebook_link = venue.facebook_link
  form.website = venue.website
  form.seeking_talent = venue.seeking_talent
  form.seeking_description = venue.seeking_description

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  venue = Venue.query.get(venue_id)
  try:
    venue.name = request.form.get('name')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.address = request.form.get('address')
    venue.phone = request.form.get('phone')
    venue.image_link = request.form.get('image_link')
    venue.genres = request.form.get('genres')
    venue.facebook_link = request.form.get('facebook_link')
    venue.website = request.form.get('website')
    venue.seeking_talent = request.form.get('seeking_talent')
    venue.seeking_description = request.form.get('seeking_description')
    db.session.commit()
  except:
    error = False
    db.session.rollback()
  finally:
    if error == True:
      db.session.close()
      flash('venue was successfully updated')
    else:
      db.session.close()
      flash('venue was not successfully updated')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  error = False
  try:
    # GET all the data from the form
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    img_link = request.form.get('image_link')
    genres = request.form.get('genres')
    facebook_link = request.form.get('facebook_link')
    website = request.form.get('website')
    seeking_venue = request.form.get('seeking_venue')
    seking_description = request.form.get('seeking_description')
    artist = Artist(name = name, city = city, state = state, phone = phone, image_link = img_link, genres = genres, facebook_link = facebook_link, website = website, seeking_venue = seeking_venue, seking_description = seking_description)
    db.sesison.add(artist)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    
  finally:
    # on successful db insert, flash success
    if error == False:
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
      db.session.close()
    else:
      flash('An error occurred. Artist could not be created.')
      db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows_query = Show.query.join(Artist).join(Venue).all()
  data = []
  for show in shows_query:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time
    })
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  error = False
  try:
    # get all the data from the form
    artist_id = request.form.get('artist_id')
    venue_id = request.form.get('venue_id')
    start_time = request.form.get('start_time')
    show = Show(artist_id = artist_id, venue_id = venue_id, start_time = start_time)
    db.session.add(show)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    if error == False:
      # on successful db insert, flash success
      flash('Show was successfully listed!')
      db.session.close()
    else:
      flash('Show could not be created')
      db.sesison.close()
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
