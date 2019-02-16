"Vibez"
from pprint import pformat
import os

import requests

from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Song, Playlist, SongPlaylist

import spotify

app = Flask(__name__)

#This secret key is required to use FLask sesssions and the debug toolbar
app.secret_key = "youcandothisjen"

#The line of code below will raise an error when you use an undefined variable in Jinja2 (
# instead of failing)
app.jinja_env.undefined = StrictUndefined



@app.route("/")
def index():
    """Homepage for those not logged in"""

    return render_template("homepage.html")

@app.route("/homepageloggedin")
def homepage_loggedin():
    """Homepage for those who are logged in"""

    return render_template("homepage_loggedin.html")



@app.route('/register')
def register_form():
    """Show form for user signup"""

    return render_template("register.html")

@app.route('/register', methods=['POST'])
def register_process():
    """Process registration"""

    #Get form variables
    fname = request.form["fname"]
    lname = request.form["lname"]
    email = request.form["email"]
    password = request.form["password"]

    user = db.session.query(User).filter(User.email == email).first()
    
    if user:
            flash("User already exists")
            redirect("/")
    else:
        new_user = User(fname=fname, lname=lname, email=email, password=password)

        db.session.add(new_user)
        db.session.commit()

        flash(f"User {fname} has been added.")
        return redirect("/login")

@app.route('/login')
def login_form():
    """Show login form."""

    return render_template("login.html")

@app.route('/login', methods=['POST'])
def login_process():
    """Process login"""

    #Get form variables
    email = request.form["email"]
    password = request.form["password"]

    user = User.query.filter_by(email=email).first()

    if not user:
        flash("No such user")
        return redirect("/login")
    
    if user.password != password:
        flash("Incorrect password")
        return redirect("/login")
    
    #this is the session id in which it determines whether user 
    #is logged in and is allowed to navigate said pages
    session["user_id"] = user.user_id

    flash("Logged in")
    return redirect("/homepage_loggedin")

@app.route('/logout')
def logout():
        """Log out."""

        del session["user_id"]
        flash("Logged Out.")
        return redirect("/")
    
# @app.route("/users")  #A route to check out other user's playlists
# def user_list():
#         """Show list of users"""

#         users = User.query.all()
#         return render_template("user_list.html", users=users)
    
@app.route("/userplaylist")
def user_playlists(user_id):
    """Show info about user's playlists."""

@app.route("/create")
def create_playlist():
    """Create playlist by selecting genre, danceability, and speechiness"""

    if session.get("user_id") is not None:
        return render_template("create_playlist.html")
    else:
        flash("User may create playlist after logging in")
        return redirect("/")

@app.route("/create", methods=['POST'])
def created_playlist():
    """Save playlist to user personal profile"""

    genre = request.form.get("genre")
    min_danceability = request.form.get("minDanceability")
    max_danceability = request.form.get("maxDanceability")


    #save as session so you can later see page of newly generated playlist
    session["genre"] = genre
    session["minimum_danceability"] = min_danceability
    session["maximum_danceability"] = max_danceability

    return redirect("/generateplaylist")

#     permanently save the generated playlist into database


@app.route("/generateplaylist")
def generate_playlist():
    
    spotify_info = spotify.base_playlist(spotify.generate_token(), session["genre"], session["minimum_danceability"], session["maximum_danceability"])
    print(spotify_info)

    playlist = Playlist(user_id=session["user_id"], playlist_image=spotify_info["tracks"][0]["album"]["images"][1]["url"], playlist_genre=session["genre"], playlist_mindanceability=session["minimum_danceability"],
                        playlist_maxdanceability=session["maximum_danceability"])
    db.session.add(playlist)
    db.session.commit()

    #store songs into Song database and song-playlist data into SongPlaylist database
    for track in spotify_info["tracks"]:

        #if Song database is empty, add generated song as new song in the database 
        if len(db.session.query(Song).all()) <= 0:
            song = Song(track_id=track["id"], track_title=track["name"], artist=[artist["name"] for artist in track["artists"]])
            db.session.add(song)
            db.session.commit()
        #if a song(s) exists in the database, check to see if there is a match with generated song
        #and existing song(s) match. If there is no match, add generated song as new song in the database.
        #Both if statements check to make sure new songs that are added into database do not already
        #exist in the database.
        if len(db.session.query(Song).filter(Song.track_id == track["id"]).all()) <= 0:
            song = Song(track_id= track["id"] , track_title= track["name"] , artist= [artist["name"] for artist in track["artists"]])
            db.session.add(song)
            db.session.commit()
        songplaylist = SongPlaylist(track_id= track["id"], playlist_id= playlist.playlist_id)
        db.session.add(songplaylist)
        db.session.commit()

   

    #reveal newly generated playlist on generate_playlist.html page based on stored session from user input above
    return render_template("generate_playlist.html", spotify_info = spotify_info)


    


@app.route("/playlists")
def playlists():
    """Show list of user's playlists"""

    if session.get("user_id") is not None:
        playlists = db.session.query(Playlist).filter(Playlist.user_id == session.get("user_id")).order_by(Playlist.playlist_id).all()
        return render_template("user_playlists_page.html", playlists = playlists)
    else:
        flash("User may view their playlist after logging in")
        return redirect("/login")

@app.route("/playlists", methods=["POST"])
def choose_playlists():
    """Get playlist id to connect to different songs associated with id and display
    songs in the following page"""

    playlist_id = request.form.get("playlistId")
    print(playlist_id)
    songs = db.session.query(SongPlaylist).filter(SongPlaylist.playlist_id == playlist_id).all()
    track_ids = []
    for song in songs:
        track_ids.append(song.track_id)
    string_track_ids = ','.join(track_ids)
    session["track_ids"] = string_track_ids
    return redirect("/songspage")


@app.route("/songspage")
def songs():
    """Show list of songs in playlist that user clicked on""" 

    if session.get("user_id") is not None and session.get("track_ids") is not None:
        saved_spotify_info = spotify.saved_songs(spotify.generate_token(), session["track_ids"])
            
        return render_template("user_songs_page.html", saved_spotify_info = saved_spotify_info)








if __name__ == "__main__":
# We have to set debug=True here, since it has to be True at the point
# that we invoke the DebugToolbarExtension

#Do not debug for demo
        app.debug = True

        connect_to_db(app)

#Use the DebugToolbar
        DebugToolbarExtension(app)

        app.run(host="0.0.0.0")



  