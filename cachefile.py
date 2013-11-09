class CacheFile:
	def __init__(self,directory,date,size):
		self.directory = directory
		temp = self.directory.split('/')
		self.name = temp[-1]
		self.date = date
		self.size = size

	