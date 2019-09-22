import requests
from os import getenv
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from flask import Flask, escape, request

load_dotenv()

app = Flask(__name__, static_url_path='/public')

import routes
