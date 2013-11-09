# Include the Dropbox SDK
import dropbox
from cachefile import *
import datetime
import os
# Get your app key and secret from the Dropbox developer website
app_key = '4zpvumln2nqv1ue'
app_secret = 'qpyofecy9vnu5m3'
APP_FOLDER = '/c'
KEY = lambda cache_file: cache_file.date
DIRECTORY = "~/Documents"
CUTOFF = 7


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

def getAvailableSpace():
	nonlocal FREE_SPACE
	client = authenticate()
	totalSpace = client.account_info()['quota_info']['quota']
	normalSpace = client.account_info()['quota_info']['normal']
	sharedSpace = client.account_info()['quota_info']['shared']
	freeSpace = totalSpace - normalSpace - sharedSpace - 52428800
	print 'linked account: ', client.account_info()['quota_info']['quota']
	return freeSpace


def file_sort(fileList, sortKey):
	return sorted(fileList,key=sortKey)

def getSortedList():
	return file_sort(accessed_recently(DIRECTORY, CUTOFF), KEY)

def trimList(client):
	nonlocal CACHED_ITEMS
	addedSpace = 0
	getAvailableSpace(client) 
	sortedList = getSortedList()
	finalList = []
	for fileToAdd in sortedList:
		if (addedSpace + fileToAdd.size) < (FREE_SPACE):
			finalList.append(fileToAdd)
			addedSpace += fileToAdd.size
	return reverse(finalList)

def addFiles(finalList,client):
	for cacheFile in finalList:
		f = open(cacheFile.directory, 'r')
		response = client.put_file(cacheFile.name, f)

def shrinkPartition(client):
	freeSpace = getAvailableSpace(client)
	folder_metadata = client.metadata('/')
	cacheFiles = []
	format = '%a, %d %b %Y %X %Z'
	for meta in folder_metadata:
		cacheFiles.append((meta['path'],strptime(meta['modified'],format)))
	cacheFiles.sort(key=lambda x: x[1])
	while freeSpace <= 0:
		client.file_delete(cacheFiles[-1][0])
		cacheFiles.pop()
		freeSpace=getAvailableSpace(client)




def main():
	date1 = datetime.date.today()
	cacheFile = CacheFile('./test.c', date1, 1)
	finalList = [cacheFile]
	addFiles(finalList, authenticate())

if __name__ == "__main__":
	main()