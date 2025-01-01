from flask import Flask, request
import validators
import os
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID
from dotenv import load_dotenv
from appwrite.query import Query
import random

load_dotenv()
client = Client()

API_KEY = os.getenv("APPWRITE_API_KEY", None)
if API_KEY is None:
    raise Exception("Please populate the environment variable `APPWRITE_API_KEY`")

APPWRITE_API_ENDPOINT = os.getenv("APPWRITE_API_ENDPOINT", None)
if APPWRITE_API_ENDPOINT is None:
    raise Exception("Please populate the environment variable `APPWRITE_API_ENDPOINT`")

APPWRITE_PROJECT_ID = os.getenv("APPWRITE_PROJECT_ID", None)
if APPWRITE_PROJECT_ID is None:
    raise Exception("Please populate the environment variable `APPWRITE_PROJECT_ID`")

APPWRITE_DB_ID = os.getenv("APPWRITE_DB_ID", None)
if APPWRITE_DB_ID is None:
    raise Exception("Please populate the environment variable `APPWRITE_PROJECT_ID`")

APPWRITE_COLLECTION_ID = os.getenv("APPWRITE_COLLECTION_ID", None)
if APPWRITE_COLLECTION_ID is None:
    raise Exception("Please populate the environment variable `APPWRITE_COLLECTION_ID`")

(client
  .set_endpoint(APPWRITE_API_ENDPOINT) # API Endpoint
  .set_project(APPWRITE_PROJECT_ID) 
  .set_key(API_KEY)
)

databases = Databases(client)

app = Flask(__name__)


@app.route('/shorten', methods=["POST"])
def shorten():
    """
    API Endpoint for shortening URL
    """
    err = "No JSON data found"
    url = ''
    if request.method != "POST":
        return 400, "Expected a POST request"
    try:
        data = request.get_json(force=True)
        
        if not "long-url" in data.keys():
            err = "Missing parameter 'long-url'"
            raise Exception(err)
        
        if not validators.url(data["long-url"]):
            err = "Invalid URL"
            raise Exception(err)
        
        url = data['long-url']
    except Exception as e:
        return e, 400
    else:
        shorty = db_put(url)
        return shorty, 200
    
@app.route('/redirect/<shorty>')
def redirect(shorty):
    """Get url to the long url

    Args:
        shorty (str): The short code

    Returns:
        long_url: Long url
    """
    if request.method != 'GET':
        return 'Expected a POST request', 400
    if len(shorty) != 5:
        return 'Short URL is not valid', 403
    is_present = is_url_present(shorty)
    if not is_present:
        return 'Short URL is not registered', 403
    return get_long_url(shorty), 200

def db_put(url): # TODO: Put url into db
    shorty = gen_shorty()
    document = databases.create_document(APPWRITE_DB_ID, APPWRITE_COLLECTION_ID, ID.unique(), {'long-url': url, 'key': shorty, 'monthly-click': 0, 'weekly-click': 0})
    return shorty

def is_url_present(short_code): # TODO: Check if url is present in db
    doc = get_long_url(short_code)
    if doc: # FIXME: Check data query
        return True
    return False

def get_long_url(short_code): # TODO: Get the long url against short code
    doc = databases.list_documents(APPWRITE_DB_ID, APPWRITE_COLLECTION_ID, [Query.equal('key', short_code)])
    return doc['documents'][0]['long-url']
    # return doc

def gen_shorty():
    tmp = ''
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    for i in range(5):
        r = random.randint(0, 61)
        tmp += chars[r]

    return tmp