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

	def write_file(self):
		"""
		Create LaTeX document containing bill of materials.

		input:			none;
		return:			none.
		"""
		hndFile = open(self.fileName, 'w')
		self.__write_header(hndFile)

		prevType = ''
		for elem in self.sortedKeys:
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
		hndFile.close()

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
