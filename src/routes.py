from app import app
from helpers import generate_random_string
from flask import make_response, redirect
from urllib.parse import urlencode
from dotenv import load_dotenv
from os import getenv

load_dotenv()

state_key = "spotify_auth_state"
spotify_client_id = getenv("SPOTIFY_CLIENT_ID")
spotify_redirect_uri = getenv("SPOTIFY_REDIRECT_URI")

@app.route("/")
@app.route("/index")
def index():
  return "Hello, World"

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

  resp = make_response(redirect("https://accounts.spotify.com/authorize?" + query_string))
  resp.set_cookie(state_key, state)

  return resp