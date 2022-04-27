from flask import Flask, request, url_for, session, redirect, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time


app = Flask(__name__)
app.secret_key = "Sksdjhskdhskhd"

CLIENT_ID="77aba330be404a389dcfa8229e53d203"
CLIENT_SECRET="a827686bd3f042f89af3f56fcc1e4c82"
SCOPE = "user-top-read"

@app.route('/')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route("/redirect")
def redirectPage():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    return redirect(url_for('wrapped', _external=True))

@app.route("/wrapped")
def wrapped():
    try:
        token_info = get_token()
    except:
        print("user not logged in")
        return redirect("/")
    sp = spotipy.Spotify(auth=token_info["access_token"])
    
    track_data = sp.current_user_top_tracks(limit=50, offset=0)['items']
    track_names = [track['name'] for track in track_data]
    artist_data = sp.current_user_top_artists(limit=50, offset=0)['items']
    artists = [item['name'] for item in artist_data]

    # Get Genre data
    genres = {}
    genres_condensed = {}
    for artist in artist_data:
        for genre in artist['genres']:
            if genre in genres:
                genres[genre] += 1
            else:
                genres[genre] = 1
    
    # remove infrequent genres
    for genre in genres:
        if genres[genre] != 1:
            genres_condensed[genre] = genres[genre]

    return render_template("index.html", tracks=track_names, artists=artists, genres=genres_condensed)


def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=url_for("redirectPage", _external=True),
        scope=SCOPE
    )

def get_token():
    token_info = session.get("token_info", None)
    if not token_info:
        raise "exception"
    now = int(time.time())

    is_expired = token_info["expires_at"] - now < 60
    if is_expired:
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
    return token_info