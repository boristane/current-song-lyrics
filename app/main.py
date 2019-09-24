import requests
from os import getenv
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from flask import Flask, escape, request

load_dotenv()
port = getenv("PORT")

app = Flask(__name__, static_url_path='/', static_folder="static", template_folder="templates")

from routes import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
