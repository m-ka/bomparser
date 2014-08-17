import os

class RefDesParser:
	def __init__(self, fileName = None):
		self.dictDescription = {}
		self.__OpenFile(fileName)

	def __OpenFile(self, fileName):
		if fileName == None or os.access(fileName, os.F_OK) == False:
			return

		f = open(fileName)
		while True:
			line = f.readline()
			if len(line) == 0:
				# Zero length indicates EOF
				break
			# Ignore lines containing comments (line starts with # sign) 
			# and lines which seem not to be formatted correctly
			if line.strip().startswith('#') or line.find(':') == -1:
				continue
			else:
				splits = line.split(':', 1)
				refdes = splits[0].strip().upper()
				if not self.dictDescription.has_key(refdes):
					descriptions = splits[1].split(',', 1)
					stripped = [item.strip() for item in descriptions]
					self.dictDescription[refdes] = stripped
		f.close()
