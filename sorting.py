import dropbox
#####GLOBAL VARIABLES#####
DIRECTORY = "~/Documents/"
CUTOFF = 7
KEY = lambda cache_file: cache_file.date
app_key = '4zpvumln2nqv1ue' 
app_secret = 'qpyofecy9vnu5m3'
##########################
flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key,app_secret)





def file_sort(fileList,sortKey):
	return fileList.sort(sortKey)



sorted_list = file_sort(accessed_recently(DIRECTORY, CUTOFF), KEY)
