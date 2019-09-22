from app import app
from helpers import generate_random_string
from flask import make_response, redirect, request, jsonify
from urllib.parse import urlencode
from dotenv import load_dotenv
from os import getenv
import base64
import requests

load_dotenv()

state_key = "spotify_auth_state"
spotify_client_id = getenv("SPOTIFY_CLIENT_ID")
spotify_redirect_uri = getenv("SPOTIFY_REDIRECT_URI")
spotify_client_secret = getenv("SPOTIFY_CLIENT_SECRET")

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


@app.route("/get-token")
def get_token():
  code = request.args.get("code")
  state = request.args.get("state")
  stored_state = request.cookies.get(state_key)
  if state is None or state != stored_state:
    print({"error": "state_mismatch"})
    return jsonify({"error": "state_mismatch"}), 500
  auth = 'Basic ' + base64.b64encode((spotify_client_id + ':' + spotify_client_secret).encode('ascii')).decode("utf-8")
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
  response = requests.post("https://accounts.spotify.com/api/token", data=query_string, headers=headers)
  if response.status_code !== 200:
    return jsonify({ "error": "invalid_token" }), 500
  return response.json(), 200