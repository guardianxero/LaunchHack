# Include the Dropbox SDK
import dropbox
import datetime
import os
import re
from recentfiles import *

# Get your app key and secret from the Dropbox developer website
app_key = '4zpvumln2nqv1ue'
app_secret = 'qpyofecy9vnu5m3'
APP_FOLDER = '/c'
KEY = lambda cache_file: cache_file.date
DIRECTORY = os.path.expanduser('~') + "/Documents"
CUTOFF = 14
MEGABYTE_50 = 524288
BUFFER_SPACE = MEGABYTE_50


def authenticate():	
	flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)

	authorize_url = flow.start()
	print '1. Go to: ' + authorize_url
	print '2. Click "Allow" (you might have to log in first)'
	print '3. Copy the authorization code.'
	code = raw_input("Enter the authorization code here: ").strip()

	access_token, user_id = flow.finish(code)

	client = dropbox.client.DropboxClient(access_token)
	return client

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
	freeSpace = getAvailableSpace(client)
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

def main():
	client = authenticate()
	initialSpace = getAvailableSpace(client)
	while True:
		if (time.time() % 3600) < 30:
			addFiles(getFinalList(client), client)
		else:
			if (abs(initialSpace - getAvailableSpace(client)) > TOLERANCE):
				completed = shrinkPartition(client)
				if completed:
					initialSpace = getAvailableSpace(client)
		time.sleep(30)
if __name__ == "__main__":
	main()
