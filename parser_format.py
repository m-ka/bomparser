import os
import re

class FormatParser:
	def __init__(self, fileName = None):
		self.dictFormat = {}
		self.pattern = re.compile(r'(field\d{1,2})')
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
				# Check whether the string contains RefDes or Quantity field number
				element = splits[0].lower().strip()
				if element  == "refdes":
					self.dictFormat["RefDes"] = splits[1].lower().strip()
					continue
				if element == "quantity":
					self.dictFormat["Quantity"] = splits[1].lower().strip()
					continue
				listFormat = self.pattern.split(splits[1].strip())
				# Remove empty elements from the format string
				for each in listFormat:
					if not each:
						listFormat.remove(each)
				self.dictFormat[element.upper()] = listFormat
		f.close()
