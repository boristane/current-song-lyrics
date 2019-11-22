import base64
from urllib.parse import urlencode
import requests
from os import getenv
from bs4 import BeautifulSoup
from flask import Flask, escape, request, make_response, redirect, request, jsonify, send_from_directory
from bs4 import BeautifulSoup
import random
import dotenv

dotenv.load_dotenv()


app = Flask(__name__, static_url_path='/',
            static_folder="static", template_folder="templates")


def get_song_data(title, artist):
    base_url = 'https://api.genius.com'
    token = getenv("GENIUS_TOKEN")
    headers = {'Authorization': 'Bearer ' + token}
    data = {'q': title + ' ' + artist}
    try:
        data = requests.get(base_url + '/search',
                            data=data, headers=headers).json()
        for song in data["response"]["hits"]:
            if artist.lower() in song['result']['primary_artist']['name'].lower():
                return song
    except:
        return None


def get_genius_lyrics(url):
    page = requests.get(url)
    html = BeautifulSoup(page.text, 'html.parser')
    lyrics = html.find('div', class_='lyrics').get_text()
    return lyrics


def get_song_lyrics(title, artist):
    try:
        song = get_song_data(title, artist)
    except Exception as error:
        app.logger.info(
            'Error getting song data for {}, {}: {}'.format(title, artist, error))
        return
    if song:
        try:
            lyrics = get_genius_lyrics(song['result']['url'])
        except:
            return None
        return lyrics


def get_current_song(token):
    base_url = 'https://api.spotify.com/v1/me/player/currently-playing'
    headers = {'Authorization': 'Bearer ' + token}
    response = requests.get(base_url, headers=headers)
    if response.status_code != 200:
        app.logger.info("Error getting the current song")
        app.logger.info(response.status_code)
        return None
    data = response.json()
    return data


def generate_random_string(length):
    text = ""
    possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    for i in range(0, length):
        random_index = random.randint(0, len(possible) - 1)
        text += possible[random_index]
    return text


state_key = "spotify_auth_state"
spotify_client_id = getenv("SPOTIFY_CLIENT_ID")
spotify_redirect_uri = getenv("SPOTIFY_REDIRECT_URI")
spotify_client_secret = getenv("SPOTIFY_CLIENT_SECRET")


@app.route("/")
@app.route("/index")
def index():
    return send_from_directory('static', 'index.html')


@app.route("/lyrics")
def lyrics():
    return send_from_directory('static', 'lyrics.html')


@app.route("/login")
def login():
    state = generate_random_string(16)
    scope = "user-read-currently-playing user-read-playback-state"
    query = {
        "response_type": "code",
        "client_id": spotify_client_id,
        "scope": scope,
        "redirect_uri": spotify_redirect_uri,
        "state": state,
        "show_dialog": False
    }
    query_string = urlencode(query)

    resp = make_response(
        redirect("https://accounts.spotify.com/authorize?" + query_string))
    resp.set_cookie(state_key, state)

    return resp


@app.route("/get-token")
def get_token():
    code = request.args.get("code")
    state = request.args.get("state")
    stored_state = request.cookies.get(state_key)
    if state is None or state != stored_state:
        print({"error": "state_mismatch"})
        return jsonify({"error": "state_mismatch"}), 500
    auth = 'Basic ' + base64.b64encode((spotify_client_id + ':' +
                                        spotify_client_secret).encode('ascii')).decode("utf-8")
    query = {
        "code": code,
        "redirect_uri": spotify_redirect_uri,
        "grant_type": "authorization_code"
    }
    query_string = urlencode(query)
    headers = {
        "Authorization": auth,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    try:
        response = requests.post(
            "https://accounts.spotify.com/api/token", data=query_string, headers=headers)
        if response.status_code != 200:
            return jsonify({"error": "invalid_token"}), 500
    except:
        return jsonify({"error": "invalid_token"}), 500

    return response.json(), 200


@app.route("/refresh-token")
def refresh_token():
    token = request.args.get("refresh_token")
    auth = 'Basic ' + base64.b64encode((spotify_client_id + ':' +
                                        spotify_client_secret).encode('ascii')).decode("utf-8")
    query = {
        "grant_type": "refresh_token",
        "refresh_token": token
    }
    query_string = urlencode(query)
    headers = {
        "Authorization": auth,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    try:
        response = requests.post(
            "https://accounts.spotify.com/api/token", data=query_string, headers=headers)
        if response.status_code != 200:
            return jsonify({"error": "invalid_token"}), 500
    except:
        return jsonify({"error": "invalid_token"}), 500
    return response.json(), 200


@app.route('/api/current-song')
def current_song():
    token = request.args.get("token")
    try:
        song = get_current_song(token)
        if song is None:
            return jsonify({"error": "song not found"}), 204
    except:
        return jsonify({"error": "song not found"}), 204
    return jsonify(song), 200


@app.route('/api/lyrics')
def get_lyrics():
    title = request.args.get("title")
    artist = request.args.get("artist")
    lyrics = get_song_lyrics(artist=artist, title=title)
    if lyrics is None:
        return jsonify({"error": "lyrics not found"}), 204
    return jsonify(lyrics), 200
