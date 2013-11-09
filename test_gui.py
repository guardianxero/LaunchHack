#!/usr/bin/python
import urllib
import urllib2
import urlparse
import threading
import time
import webbrowser

# Get your app key and secret from the Dropbox developer website
app_key = '4zpvumln2nqv1ue'
app_secret = 'qpyofecy9vnu5m3'
APP_FOLDER = '/c'
DIRECTORY = "~/Documents"
CUTOFF = 7


class TokenData:
    def __init__(self,token,token_secret):
        self.token = token
        self.token_secret = token_secret

def mk_header_no_token():
    s = 'OAuth oauth_version="1.0", oauth_signature_method="PLAINTEXT"'
    s += ', oauth_consumer_key="{0}"'.format(app_key)
    s += ', oauth_signature="{0}&"'.format(app_secret)
    return s


def mk_header_with_token(token_key, token_secret):
    s = 'OAuth oauth_version="1.0", oauth_signature_method="PLAINTEXT"'
    s += ', oauth_consumer_key="{0}"'.format(urllib.quote_plus(app_key))
    s += ', oauth_token="{0}"'.format(urllib.quote_plus(token_key))
    s += ', oauth_signature="{0}&{1}"'.format(urllib.quote_plus(app_secret), urllib.quote_plus(token_secret))
    return s

def http_request(url, auth_header):
    req = urllib2.Request(url)
    req.add_header("Authorization", auth_header)
    return urllib2.urlopen(req).read()


def parse_token(result):
    params = urlparse.parse_qs(result, strict_parsing=True)

    token = params.get('oauth_token')
    
    token_secret = params.get('oauth_token_secret')

    if token is None or token_secret is None or len(token) != 1 or len(token_secret) != 1:
        raise ValueError, 'Invalid tokens'

    return TokenData(token[0], token_secret[0])


class PollingThread(threading.Thread):
    def __init__(self,token_data):
        super(PollingThread, self).__init__()
        self._stop = threading.Event()
        self.token_data = token_data

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def check_url_valid(self):
        try:
            r = http_request("https://api.dropbox.com/1/oauth/access_token",mk_header_with_token(self.token_data.token,self.token_data.token_secret))
            return r
        except:
            return False

    def run(self):
        valid = self.check_url_valid()
        while not valid:
            valid = self.check_url_valid()
            time.sleep(1)


def main():

    r = http_request("https://api.dropbox.com/1/oauth/request_token",mk_header_no_token())

    token_data = parse_token(r)

    authorize_url = "https://www.dropbox.com/1/oauth/authorize?oauth_token={0}".format(token_data.token)

    poll_thread = PollingThread(token_data)
    poll_thread.start()

    webbrowser.open_new(authorize_url)


if __name__ == '__main__':
    main()
