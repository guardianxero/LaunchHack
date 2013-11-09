import os
import datetime
from datetime import datetime 
from datetime import timedelta

class CacheFile:
	def __init__(self,directory,date,size):
		self.directory = directory
		self.date = date
		self.size = size

		temp=self.directory.split('/')
		self.name=temp[-1]

def unsorted_list(): ## returns unsorted list of recent files accessed 
	import datetime
	min_mtime = datetime.datetime.today()  ## sets the last date you do not want to include 
	difference=datetime.timedelta(days=50)
	min_mtime=min_mtime-difference # sets the earliest date from which the files should be
	recent_files=['git'] ## the list that will return in the form [(fullpath name,(date,filesize))]
	not_include= #creates file types that we don't want to include 
	for dirname,subdirs,files in os.walk("C:\Users\Kunal\Desktop"):
	    for fname in files:
	        full_path = os.path.join(dirname, fname)
	        mtime = os.stat(full_path).st_mtime
	        mtime=datetime.datetime.fromtimestamp(mtime)
	        templist=fullpath.split(".")
	        filetype=templist[-1]
	        if mtime > min_mtime:
	        	if filetype not in not_include:
	            	recent_files.append(CacheFile(full_path,mtime,os.path.getsize(full_path))) ## appends to the recent files list
	return recent_files
print(unsorted_list())

