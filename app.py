from flask import Flask, render_template, request, redirect, make_response,send_file
import validators
import os
import datetime
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
    try:
        data = request.get_json(force=True)
        
        if not "long-url" in data.keys():
            err = "Missing parameter 'long-url'"
            return err, 400
        
        if not validators.url(data["long-url"], consider_tld=True, private=False):
            err = "Invalid URL"
            return err, 400 
        url = data['long-url']
    except Exception as e:
        return str(e), 400
    else:
        shorty = db_put(url)
        # ret = make_response(shorty)
        # ret.headers.add("Access-Control-Allow-Origin", "*")
        # return ret, 200
        return shorty
    
@app.route('/redirect/<shorty>')
def redirect_url(shorty):
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
    doc = get_long_url(shorty)
    # Reset weekly click if the date is not within the last 7 days
    if datetime.datetime.now() - datetime.datetime.strptime(doc['documents'][0]['date-added'], "%Y-%m-%d %H:%M:%S") > datetime.timedelta(days=7):
        result = databases.update_document(APPWRITE_DB_ID, APPWRITE_COLLECTION_ID, doc['documents'][0]['$id'], {'weekly-click': 0})
    
    # Reset monthly click if the date is not within the last 30 days
    if datetime.datetime.now() - datetime.datetime.strptime(doc['documents'][0]['date-added'], "%Y-%m-%d %H:%M:%S") > datetime.timedelta(days=30):
        result = databases.update_document(APPWRITE_DB_ID, APPWRITE_COLLECTION_ID, doc['documents'][0]['$id'], {'monthly-click': 0})

    result = databases.update_document(APPWRITE_DB_ID, APPWRITE_COLLECTION_ID, doc['documents'][0]['$id'], {'monthly-click': doc['documents'][0]['monthly-click'] + 1, 'weekly-click': doc['documents'][0]['weekly-click'] + 1})
    # return {"URL": doc["documents"][0]['long-url'], "monthly-click": doc['documents'][0]['monthly-click'], "weekly-click": doc['documents'][0]['weekly-click']}
    return redirect(doc["documents"][0]['long-url'], code=302)
    # ret = make_response(shorty)
    # ret.headers.add("Access-Control-Allow-Origin", "*")
    # return ret

@app.route('/statistics/<shorty>')
def statistics(shorty):
    """Get url stats

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
    doc = get_long_url(shorty)

     # Reset weekly click if the date is not within the last 7 days
    if datetime.datetime.now() - datetime.datetime.strptime(doc['documents'][0]['date-added'], "%Y-%m-%d %H:%M:%S") > datetime.timedelta(days=7):
        result = databases.update_document(APPWRITE_DB_ID, APPWRITE_COLLECTION_ID, doc['documents'][0]['$id'], {'weekly-click': 0})
    
    # Reset monthly click if the date is not within the last 30 days
    if datetime.datetime.now() - datetime.datetime.strptime(doc['documents'][0]['date-added'], "%Y-%m-%d %H:%M:%S") > datetime.timedelta(days=30):
        result = databases.update_document(APPWRITE_DB_ID, APPWRITE_COLLECTION_ID, doc['documents'][0]['$id'], {'monthly-click': 0})
        
    
    r = {"URL": doc["documents"][0]['long-url'], "monthly-click": doc['documents'][0]['monthly-click'], "weekly-click": doc['documents'][0]['weekly-click']}
    # ret = make_response(r)
    # ret.headers.add("Access-Control-Allow-Origin", "*")
    return r

def db_put(url): # TODO: Put url into db
    shorty = gen_shorty()
    document = databases.create_document(APPWRITE_DB_ID, APPWRITE_COLLECTION_ID, ID.unique(), {'long-url': url, 'key': shorty, 'monthly-click': 0, 'weekly-click': 0, 'date-added': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    return shorty

def is_url_present(short_code): # TODO: Check if url is present in db
    doc = get_long_url(short_code)
    if len(doc['documents']) > 0: # FIXME: Check data query
        return True
    return False

def get_long_url(short_code): # TODO: Get the long url against short code
    doc = databases.list_documents(APPWRITE_DB_ID, APPWRITE_COLLECTION_ID, [Query.equal('key', short_code)])
    return doc


def gen_shorty():
    tmp = ''
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    for i in range(5):
        r = random.randint(0, 61)
        tmp += chars[r]
    
    if is_url_present(tmp):
        return gen_shorty()

    return tmp


@app.route('/')
def index():
    resp = make_response(send_file("templates/index.html"))
    resp.headers.add("Access-Control-Allow-Origin", "*")
    return resp, 200

@app.route('/stats/<shorty>')
def stats(shorty):
    short_stats = statistics(shorty)
    print(short_stats)
    return render_template("stats.html", short_stats=short_stats, shorty=shorty)