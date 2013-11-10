# Include the Dropbox SDK
import dropbox
import datetime
import os
from recentfiles import *
import time
import re
import webbrowser
from flask import Flask,request, session, g, redirect, url_for, abort, current_app
import urllib
import urllib2
import json

# Get your app key and secret from the Dropbox developer website
app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app_key = '4zpvumln2nqv1ue'
app_secret = 'qpyofecy9vnu5m3'
APP_FOLDER = '/c'
KEY = lambda cache_file: cache_file.date
DIRECTORY = os.path.expanduser('~') + "/Documents"
CUTOFF = 14
MEGABYTE_50 = 50000000 #50 MB
BUFFER_SPACE = 0 #MEGABYTE_50
TOLERANCE = 20000 #20 KB


# def authenticate():	
# 	flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)

# 	authorize_url = flow.start()
# 	print '1. Go to: ' + authorize_url
# 	print '2. Click "Allow" (you might have to log in first)'
# 	print '3. Copy the authorization code.'
# 	code = raw_input("Enter the authorization code here: ").strip()

# 	access_token, user_id = flow.finish(code)

# 	client = dropbox.client.DropboxClient(access_token)
# 	return client

def getAvailableSpace(client):
	totalSpace = client.account_info()['quota_info']['quota']
	normalSpace = client.account_info()['quota_info']['normal']
	sharedSpace = client.account_info()['quota_info']['shared']
	freeSpace = totalSpace - normalSpace - sharedSpace - BUFFER_SPACE
	print 'linked account: ', client.account_info()['quota_info']['quota']
	return freeSpace

def file_sort(fileList, sortKey):
	return sorted(fileList, key=sortKey)

def getSortedList():
	return file_sort(unsorted_list(DIRECTORY, CUTOFF), KEY)

def getFinalList(client):
	addedSpace = 0
	freeSpace = getAvailableSpace(client) 
	sortedList = getSortedList()
	finalList = []
	for fileToAdd in sortedList:
		if (addedSpace + fileToAdd.size) < (freeSpace):
			finalList.append(fileToAdd)
			addedSpace += fileToAdd.size
			print(finalList)
	finalList.reverse()
	return finalList

def addFiles(finalList,client):
	for cacheFile in finalList:
		f = open(cacheFile.directory, 'r')
		try:
			response = client.put_file(cacheFile.name, f, True)
		except dropbox.rest.ErrorResponse, e:
			pass

def shrinkPartition(client):
	freeSpace = getAvailableSpace(client) + BUFFER_SPACE
	folder_metadata = client.metadata('/')
	cacheFiles = []
	format = '%a, %d %b %Y %H:%M:%S'
	for meta in folder_metadata['contents']:
		#Get all files from app folder
		date = re.sub(r"[+-]([0-9])+", "", meta['modified']).strip()
		cacheFiles.append(CacheFile(meta['path'], datetime.strptime(date, format), meta['bytes'])) 
	#Sort by date
	cacheFiles.sort(key=KEY)
	completed = False
	while freeSpace <= 0 and len(cacheFiles)>0:
		removedFile = cacheFiles.pop()
		client.file_delete(removedFile.directory)
		freeSpace += removedFile.size
		completed = True
	return completed

def execute_cachebox(client):
	initialSpace = getAvailableSpace(client)
	while True:
		# if (time.time() % 41) < 30:
		if (time.time() % 100) < 30:
			print(getFinalList(client))
			addFiles(getFinalList(client), client)
	
		if getAvailableSpace(client) < TOLERANCE:
			print('in if')
			completed = shrinkPartition(client)
			if completed: 
				initialSpace = getAvailableSpace(client) 
		elif (abs(initialSpace - getAvailableSpace(client)) > TOLERANCE):
			completed = shrinkPartition(client)
			if completed:
				initialSpace = getAvailableSpace(client)
		time.sleep(30)

@app.route('/')
def home():
    return 'Nothing'

@app.route('/dropbox_auth_finish', methods=['GET'])
def dropbox_auth_finish():
    try:
        code = request.args.get('code')

        url = "https://www.dropbox.com/1/oauth2/token"
        values = {'code':code,
                'grant_type': 'authorization_code',
                'client_id': app_key,
                'client_secret': app_secret,
                'redirect_uri': 'http://127.0.0.1:5000/dropbox_auth_finish'}

        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        response_json = response.read()        

        
        json_dict = json.loads(response_json)
        access_token = json_dict['access_token']

        output_file = open('auth_data','w')
        output_file.write(access_token)
        output_file.close()

        client = dropbox.client.DropboxClient(str(access_token))
        execute_cachebox(client)

        return redirect(url_for('shutdown'))

    except dropbox.client.DropboxOAuth2Flow.BadRequestException, e:
        abort(400)
    except dropbox.client.DropboxOAuth2Flow.BadStateException, e:
        abort(400)
    except dropbox.client.DropboxOAuth2Flow.CsrfException, e:
        abort(403)
    except dropbox.client.DropboxOAuth2Flow.NotApprovedException, e:
        return redirect(url_for('main'))
    except dropbox.client.DropboxOAuth2Flow.ProviderException, e:
        abort(403)

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/shutdown',methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down'
def main():
    try:
        auth_data = open('auth_data').readlines()
        oauth2_token = auth_data[0]
        
        client = dropbox.client.DropboxClient(oauth2_token)
        execute_cachebox(client)
    except KeyboardInterrupt:
    	pass
    except:
        url = "https://www.dropbox.com/1/oauth2/authorize"
        data = {}
        data['response_type'] = 'code'
        data['client_id'] = app_key
        data['redirect_uri'] = 'http://127.0.0.1:5000/dropbox_auth_finish'

        url_values = urllib.urlencode(data)
        full_url = url + '?' + url_values

        webbrowser.open(full_url)

        app.run(host='127.0.0.1')

if __name__ == "__main__":
    main()