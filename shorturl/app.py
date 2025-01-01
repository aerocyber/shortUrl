from flask import Flask, request
import validators

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
        data = request.json
        if not "long-url" in data.keys():
            err = "Missing parameter 'long-url'"
            raise Exception(err)
        
        if not validators.url(data["long-url"]):
            err = "Invalid URL"
            raise Exception(err)
        
        url = data['long-url']
    except Exception:
        return 400, err
    else:
        shorty = db_put(url)
        return 200, shorty
    
@app.route('/redirect/<shorty>')
def redirect(shorty):
    """Get url to the long url

    Args:
        shorty (str): The short code

    Returns:
        long_url: Long url
    """
    if len(shorty) != 5:
        return 403, 'Short URL is not valid'
    is_present = is_url_present(shorty)
    if not is_present:
        return 403, 'Short URL is not registered'
    return 200, get_long_url(shorty)

def db_put(url): # TODO: Put url into db
    ...

def is_url_present(short_code): # TODO: Check if url is present in db
    ...

def get_long_url(short_code): # TODO: Get the long url against short code
    ...