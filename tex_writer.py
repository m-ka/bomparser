# -*- coding: utf8 -*-

import os
import re
import operator
import codecs

class Element:
	"""
		Helper class wich will be used for sorting.
	"""
	def __init__(self, refdes, element, pos):
		self.refdes = refdes
		self.element = element
		self.pos = pos

	def __repr__(self):
		return repr((self.refdes, self.element, self.pos))

class TexWriter:
	def __init__(self, settings, dictBom, dictDescription):
		self.fileName = settings["fileTex"]
		self.dictBom = dictBom
		self.dictDescription = dictDescription
		self.__firstQuote = True
		self.sortedKeys = self.__sortElements(self.dictBom.keys())
		self.groupedKeys = []
		self.groupMode = settings["group"]
		self.strings = settings["strings"]
		# This list will be used to check whether an element is unique or
		# there are other elements of the same type
		self.elementTypes = [re.sub('[0-9]', '', elem) for elem in self.sortedKeys]

		self.latexSpecial = {
			'&': '\&',
			'%': '\%',
			'$': '\$',
			'#': '\#',
			'_': '\_',
			'{': '\{',
			'}': '\}',
			'"': '',
			'~': '\lettertilde{}',
			'^': '\letterhat{}',
			'\\': '\letterbackslash{}',
			'\n': '\\\\',
		}
		self.__combineElements()

	def write_file(self):
		"""
		Create LaTeX document containing bill of materials.

		input:			none;
		return:			none.
		"""
		hndFile = codecs.open(self.fileName, mode='w', encoding='utf-8')
		self.__write_header(hndFile)

		if self.groupMode == "none":
			self.__writeUngrouped(self.sortedKeys, hndFile)
		else:
			self.groupedKeys = self.__combineElements()
			self.__writeGrouped(self.groupedKeys, hndFile)
		hndFile.close()

	def __writeUngrouped(self, listKeys, hndFile):
		"""
			Write ungrouped list of elements to file.

			listKeys:	a list of ungrouped refdes,
			hndFile:	a descriptor to open file,
			return:		none.
		"""
		prevType = ''
		stringCounter = self.strings
		for elem in listKeys:
			elemType = re.sub('[0-9]', '', elem)
			if elemType != prevType:
				self.__write_section(hndFile, elemType)
				prevType = elemType
				stringsCounter = self.strings

			elemString = ['\\Element{']
			currentElem = self.dictBom[elem]
			# Find and convert special character in the string
			convertedStr = []
			for part in currentElem[0]:
				for char in part:
					convertedStr.append(self.__escape_latex(char))
			elemString.extend(convertedStr)
			elemString.extend(["}{\\refbox{", elem, "}}{", currentElem[-1], "}"])
			beautyStr = self.__beautifyStr(''.join(elemString))
			hndFile.write(beautyStr.decode("utf-8"))
			hndFile.write('\n')
			if self.strings != 0:
				stringsCounter -= 1
				if stringsCounter == 0:
					self.__writeEmptyString(hndFile)
					stringsCounter = self.strings

		self.__write_footer(hndFile)

	def __writeGrouped(self, listKeys, hndFile):
		"""
			Write grouped list of elements to file.

			listKeys:	a list of grouped refdes,
			hndFile:	a descriptor to open file,
			return:		none.
		"""
		prevType = ''
		stringsCounter = self.strings
		for elem in listKeys:
			elemType = re.sub('[0-9]', '', elem[0])
			if elemType != prevType:
				self.__write_section(hndFile, elemType)
				prevType = elemType
				stringsCounter = self.strings

			elemString = ['\\Element{']
			currentElem = self.dictBom[elem[0]]
			# Find and convert special character in the string
			convertedStr = []
			for part in currentElem[0]:
				for char in part:
					convertedStr.append(self.__escape_latex(char))
			elemString.extend(convertedStr)
			elemString.append("}{")

			# Choose the representation of RefDes in the corresponding field
			if len(elem) == 1:
				# There is the only element in the elem. Proceed without modufication
				refdeselem = ''.join(['\\refbox{', elem[0], '}'])
			if len(elem) == 2:
				# There are two elements in the elem. Separate them with comma.
				refdes = ', '.join(elem)
				refdeselem = ''.join(['\\refbox{', refdes, '}'])
			if len(elem) == 3:
				# There are three elements in the elem. Deside upon ellipsis or
				# comma separated list
				refdes = ', '.join(elem)
				if len(refdes) > 9:
					# Resulting string is too long, let's elem it
					refdes = ''.join([elem[0], '\ldots{}', elem[-1]])
				refdeselem = ''.join(['\\refbox{', refdes, '}'])
			if len(elem) > 3:
				refdeselem = ''.join(['\\refbox{', elem[0], '\ldots{}', elem[-1], '}'] )

			elemString.extend(refdeselem)
			elemString.extend('}')

			# Add the number of elements
			elemString.extend(["{", str(len(elem)), "}"])
			beautyStr = self.__beautifyStr(''.join(elemString))
			hndFile.write(beautyStr.decode("utf-8"))
			hndFile.write('\n')
			if self.strings != 0:
				stringsCounter -= 1
				if stringsCounter == 0:
					self.__writeEmptyString(hndFile)
					stringsCounter = self.strings

		self.__write_footer(hndFile)

	def __writeEmptyString(self, hndFile):
		"""
			Add an empty string to resulting file.
			hndFile:	a descriptor to open file,
			return:		none.
		"""
		string = "\\Element{}{}{}\n"
		hndFile.write(string.decode("utf-8"))

	def __findSequences(self, refdes):
		"""
			Find consequent sequences in a list of refdes and group them into a
			separate list.

			listKeys:	a list of refdes,
			return:		a list containing consequent refdes grouped into lists.
		"""
		listKeys = list(refdes)
		groupedKeys = []
		currentGroup = []
		for index in range(len(listKeys)):
			if index == 0:
				currentGroup.append(listKeys[0])
				prevNum = int(re.sub('[A-Z/-/_/.]', '', listKeys[0]))
				continue
			currentNum = int(re.sub('[A-Z/-/_/.]', '', listKeys[index]))
			if currentNum == prevNum + 1:
				currentGroup.append(listKeys[index])
			else:
				groupedKeys.append(currentGroup)
				currentGroup = [listKeys[index]]
			prevNum = currentNum
		groupedKeys.append(currentGroup)

		return groupedKeys

	def __write_header(self, hndFile):
		"""
			Write LeTeX document header.

			hndFile:	the handler of open file;
			return:		none.
		"""
		hndFile.write(u"\\documentclass[doctype=pe,compactmode]{pcbdoc}\n")
		hndFile.write(u"\\AuthorSet{Пупкин}\n")
		hndFile.write(u"\\CheckerSet{Ближайший}\n")
		hndFile.write(u"\\NormControllerSet{Суровый}\n")
		hndFile.write(u"\\ApproverSet{Сказочник}\n")
		hndFile.write(u"\\NameSet{Фильтр}\n")
		hndFile.write(u"\\NumberSet{РОГА.12345.001}\n")

		hndFile.write(u"\\begin{document}\n")
		hndFile.write(u"\\begin{ElementList}\n")

	def __write_footer(self, hndFile):
		"""
			Write LaTeX document footer.

			hndFile:	the handler of open file;
			return:		none.
		"""
		hndFile.write("\\end{ElementList}\n")
		hndFile.write("\\end{document}\n")

	def __write_section(self, hndFile, refdes):
		"""
			Write new section header to the file based on the RefDes descriptions.

			hndFile:	the handler of open file;
			refdes:		refdes of an element for which new section will be created;
			return:		none.
		"""
		header = ['\\Part{']
		element = re.sub('[0-9]', '', refdes)
		if element in self.dictDescription.keys():
			if self.elementTypes.count(element) > 1:
				count = 1
			else:
				count = 0
			# Check whether descrition contains the requered string or not
			if len(self.dictDescription[element]) - 1 >= count:
				header.extend(self.dictDescription[element][count])
				header.append('}')
				hndFile.write(''.join(header).decode("utf-8"))
				hndFile.write('\n')

	def __escape_latex(self, char):
		"""
			Escape special characters in LaTeX document.

			symbol:		symbol to convert;
			return:		escaped symbol in case it has special meaning,
						or the same symbol otherwise.
		"""
		if char in self.latexSpecial.keys():
			# Replace quotes with russian typographic symbol
			if char != '"':
				return self.latexSpecial[char]
			else:
				if self.__firstQuote:
					self.__firstQuote = False
					return '<<'
				else:
					self.__firstQuote = True
					return '>>'
		else:
			return char

	def __sortElements(self, elements):
		"""
			Sorts a list of elements.

			elements:	unsorted list of elements;
			return:		sorted list of elements.
		"""
		# Separate the type of an element from its position number
		elemList = []
		for refdes in elements:
			elemType = re.sub('[0-9]', '', refdes)
			elemPos = int(re.sub('[A-Z\-\_\.]', '', refdes.upper()))
			elemList.append(Element(refdes, elemType, elemPos))
		# Sort elements in two stages
		elemList = sorted(elemList, key = operator.attrgetter('pos'))
		elemList = sorted(elemList, key = operator.attrgetter('element'))
		return [elem.refdes for elem in elemList]

	def __combineElements(self):
		"""
			Combine elements in a sorted list into groups.
			input:		none, this method operates on class member;
			return:		none.
		"""
		refdes = list(self.sortedKeys)
		groupedKeys = []
		for currentElement in refdes:
			if (len(refdes) == refdes.index(currentElement) + 1):
				# We've reached the end of list
				pass
			else:
				process = True
				offset = 1
				currentType = re.sub('[0-9]', '', currentElement)
				currentStr = self.dictBom[currentElement][0]
				currentGroup = []
				currentGroup.append(currentElement)
				while process is True:
					# Compare elements' types and process them in case they are identical
					nextElement = refdes[refdes.index(currentElement) + offset]
					nextType = re.sub('[0-9]', '', nextElement)
					if (currentType == nextType):
						nextStr = self.dictBom[nextElement][0]
						if len(currentStr) == len(nextStr):
							matched = 0
							for part in zip(currentStr, nextStr):
								if part[0] == part[1]:
									matched += 1
								else:
									break
							if matched == len(currentStr):
								currentGroup.append(nextElement)
								refdes.remove(nextElement)
								# Check whether we've reached the end of list
								if (len(refdes) < refdes.index(currentElement) + offset + 1):
									break
							else:
								process = False
						else:
							process = False
					else:
						process = False
				if currentGroup:
					groupedKeys.append(currentGroup)
		return groupedKeys

	def __beautifyStr(self, elem):
		"""
			Remove excessive commas and spaces from string.

			elem:		the string to process;
			return:		processed string.
		"""
		# Remove leading or trailing commas and spaces
		elem = re.sub('^[, ]*|[, ]*$', '', elem)
		# Replace the sequences of commas with just one 
		# corresponding symbol
		elem = re.sub(',{2,}', ',', elem)
		elem = re.sub('(, ){2,}', ', ', elem)
		# Remove excessive spaces
		elem = re.sub('( ){2,}', ' ', elem)
		# Remove spaces before comma
		elem = re.sub(' *,', ',', elem)
		# Put mathematical plus-minus symbol
		elem = re.sub('\+-|\+\\-|\+/-', "$\\pm$", elem)
		return elem
