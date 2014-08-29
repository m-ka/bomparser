# -*- coding: utf8 -*-

import re
import csv

class BomParser:
	def __init__(self, fileBom, dictFormat, dictDescription):
		self.dictFmt = dictFormat
		self.dictDsc = dictDescription
		self.fileBom = fileBom
		self.data = {}
		self.exceptions = []
		self.ParseData()

	def __create_converter(self, fields):
		"""
			The method constructs a conversion dictionary wich allows
			mapping of the internal fields replresentation to according fields in the BOM file.

			fields:		a list of field names extracted from BOM file;
			return:		a dictionary containing the mapping.
		"""
		dictMapping = {}
		counter = 1
		for elem in fields:
			name = ''.join(["field", str(counter)])
			dictMapping[name] = elem
			counter += 1
		return dictMapping

	def __get_element_type(self, elem):
		"""
			The method parses the input string and returns the type of element or elements
			defined in it.

			elem:		string of RefDes;
			return:		a string containing the type of element.
		"""
		element = elem.split(',')[0]
		element = re.sub('[0-9]', '', element)
		return element

	def __get_refdes(self, refdes):
		"""
			Splits the refdef string into separate elements.

			refdes:		string containing comma separated refdefs;
			return:		a list of refdefs.
		"""
		elements = refdes.split(',')
		elements = [elem.strip() for elem in elements]
		return elements

	def __compose_name_str(self, listFormat, dictConverter):
		"""
			Composes the name string from its format string and the mapping given.

			listFormat:	a list of fields wich should compose the name string;
			dictConverter:	mapping dictionary.
			return:		a list of composed elements.
		"""
		name = []
		for elem in listFormat:
			if elem in dictConverter.keys():
				value = dictConverter[elem]
				if value is not None and len(value) > 0:
					name.append(value)
			else:
				name.append(elem)
		return name

	def __dump_data(self):
		"""
			Utility method. It just dumps the data parsed to a text file.

			input:		none;
			return:		none.
		"""
		f = open("dump", 'w')
		name = []
		for key, value in self.data.items():
			for elem in value:
				name.append(''.join(elem))
			name.insert(0, key)
			name.append("\n")
			f.write(' '.join(name))
			name = []
		f.close()

	def ParseData(self):
		csvfile = open(self.fileBom, 'rb')
		reader = csv.DictReader(csvfile)
		converter = self.__create_converter(reader.fieldnames)
		for line in reader:
			field = converter[self.dictFmt["RefDes"]]
			elemRefDes = line[field]
			field = converter[self.dictFmt["Quantity"]]
			elemQuantity = line[field]
			elemType = self.__get_element_type(elemRefDes)
			# Iterate through format string and compose resulting string
			if elemType not in self.exceptions:
				if elemType in self.dictFmt.keys() or self.dictFmt.has_key('*'):
					# Use default format string for this element in case there is no
					# dedicated format string
					if not self.dictFmt.has_key(elemType):
						elemType = '*'
					nameFormat = self.dictFmt[elemType]
					nameTemplate = self.__compose_name_str(nameFormat, converter)
					nameStr = self.__compose_name_str(nameTemplate, line)
					for each in self.__get_refdes(elemRefDes):
						self.data[each] = [nameStr, '1']
				else:
					self.exceptions.append(elemType)
					print "Отсутствует формат строки описания для элемента ", elemType
		self.__dump_data()
