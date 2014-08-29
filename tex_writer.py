# -*- coding: utf8 -*-

import os
import re
import operator

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
	def __init__(self, fileName, dictBom, dictDescription):
		self.fileName = fileName
		self.dictBom = dictBom
		self.dictDescription = dictDescription
		self.__firstQuote = True
		self.sortedKeys = self.__sortElements(self.dictBom.keys())
		self.groupedKeys = []
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
		hndFile = open(self.fileName, 'w')
		self.__write_header(hndFile)

		# A stub goes here. The list will be selected in accordance to 
		# parameter read from configuration file. This functionality is not implemented yet.
		if False:
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
		for elem in listKeys:
			elemType = re.sub('[0-9]', '', elem)
			if elemType != prevType:
				self.__write_section(hndFile, elemType)
				prevType = elemType

			elemString = ['\\Element{']
			currentElem = self.dictBom[elem]
			# Find and convert special character in the string
			convertedStr = []
			for part in currentElem[0]:
				for char in part:
					convertedStr.append(self.__escape_latex(char))
			elemString.extend(convertedStr)
			elemString.extend(["}{\\refbox{", elem, "}}{", currentElem[-1], "}"])
			hndFile.write(''.join(elemString))
			hndFile.write("\n")

		self.__write_footer(hndFile)

	def __writeGrouped(self, listKeys, hndFile):
		"""
			Write grouped list of elements to file.

			listKeys:	a list of grouped refdes,
			hndFile:	a descriptor to open file,
			return:		none.
		"""
		prevType = ''
		for elem in listKeys:
			elemType = re.sub('[0-9]', '', elem[0])
			if elemType != prevType:
				self.__write_section(hndFile, elemType)
				prevType = elemType

			elemString = ['\\Element{']
			currentElem = self.dictBom[elem[0]]
			# Find and convert special character in the string
			convertedStr = []
			for part in currentElem[0]:
				for char in part:
					convertedStr.append(self.__escape_latex(char))
			elemString.extend(convertedStr)
			elemString.append("}{%\n")

			sequences = self.__findSequences(elem)
			print "==>"
			print elem
			for group in sequences:
				print group
				# Choose the representation of RefDes in the corresponding field
				if len(group) == 1:
					# There is the only element in the group. Proceed without modufication
					refdesGroup = ''.join(['\\refbox{', group[0], '}'])
				if len(group) == 2:
					# There are two elements in the group. Separate them with comma.
					refdes = ', '.join(group)
					refdesGroup = ''.join(['\\refbox{', refdes, '}'])
				if len(group) == 3:
					# There are three elements in the group. Deside upon ellipsis or
					# comma separated list
					refdes = ', '.join(group)
					if len(refdes) > 9:
						# Resulting string is too long, let's group it
						refdes = ''.join([group[0], '\ldots{}', group[-1]])
					refdesGroup = ''.join(['\\refbox{', refdes, '}'])
				if len(group) > 3:
					refdesGroup = ''.join(['\\refbox{', group[0], '\ldots{}', group[-1], '}'] )
				# Don't append new line character after last element
				if sequences.index(group) != len(sequences) - 1:
					elemString.extend([refdesGroup, '\n'])
				else:
					elemString.extend(refdesGroup)

			elemString.extend('}')

			# Calculate the number of elements
			count = 0
			for group in sequences:
				count = count + len(group)
			elemString.extend(["{", str(count), "}"])
			hndFile.write(''.join(elemString))
			hndFile.write("\n")

		self.__write_footer(hndFile)

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
		hndFile.write("\\documentclass[doctype=pe]{pcbdoc}\n")
		hndFile.write("\\AuthorSet{Пупкин}\n")
		hndFile.write("\\CheckerSet{Ближайший}\n")
		hndFile.write("\\NormControllerSet{Суровый}\n")
		hndFile.write("\\ApproverSet{Сказочник}\n")
		hndFile.write("\\NameSet{Фильтр}\n")
		hndFile.write("\\NumberSet{РОГА.12345.001}\n")

		hndFile.write("\\begin{document}\n")
		hndFile.write("\\begin{ElementList}\n")

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
				hndFile.write(''.join(header))
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
								if (len(refdes) != refdes.index(currentElement) + offset + 1):
									offset += 1
								else:
									process = False
						else:
							if (len(refdes) != refdes.index(currentElement) + offset + 1):
								offset += 1
							else:
								process = False
					else:
						process = False
				if currentGroup:
					groupedKeys.append(currentGroup)
		return groupedKeys
