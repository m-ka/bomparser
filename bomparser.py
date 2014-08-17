#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import re
import sys
import getopt
from parser_refdes import RefDesParser
from parser_format import FormatParser
from parser_bom import BomParser
from tex_writer import TexWriter


def PrintHelp():
	print "НАЗВАНИЕ"
	print "\tbomparser - сценарий для конвертации списка материалов (BOM) в перечень элементов.\n"
	print "СИНТАКСИС"
	print "\tbomparser [-f файл | -d файл] файл\n"
	print "ОПИСАНИЕ"
	print "bomparser преобразует список материалов (BOM), представленный в формате CSV, в перечень элементов в формате LaTeX в соответствии с правилами, заданными в файлах настроек. Файлы настроек (""description"" и ""format"") могут находиться в одном каталоге со сценарием, и в этом случае нет необходимости передавать их сценарию через параметры командной строки.\n"

def main(argv):
	fileFormat = None
	fileDescription = None
	fileBom = None

	try:
		opts, args = getopt.getopt(argv, "hf:d:", ["help", "format=", "description="])
	except getopt.GetoptError as err:
		print str(err)
		PrintHelp()
		sys.exit(2)
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			PrintHelp()
			sys.exit()
		elif opt in ("-f", "--format"):
			fileFormat = arg
		elif opt in ("-d", "--description"):
			fileDescription = arg

	if fileFormat == None:
		if os.access("format", os.F_OK):
			fileFormat = "format"
		else:
			print "Не указан файл, содержаший формат описания наименования элементов. Введите ""bomparser -h"" для справки"
			sys.exit()
	if fileDescription == None:
		if os.access("description", os.F_OK):
			fileDescription = "description"
		else:
			print "Не указан файл, содержащий описания элементов."
			sys.exit()
	if args:
		fileBom = []
		for elem in args:
			if os.access(elem, os.F_OK):
				fileBom.append(elem)
		if not fileBom:
			print "Невозможно открыть указанный BOM."
			sys.exit()
	else:
		if os.access("bom", os.F_OK) == True:
			fileBom = ["bom"]
		else:
			PrintHelp()
			sys.exit()

	fmt = FormatParser(fileFormat)
	if not fmt.dictFormat:
		print "Не удалось прочитать файл, содержаший формат описания наименования элементов."
		sys.exit()
	dsc = RefDesParser(fileDescription)
	if not dsc.dictDescription:
		print "Не удалось прочитать файл, содержащий описания элементов."
		sys.exit()
	for elem in fileBom:
		bom = BomParser(elem, fmt.dictFormat, dsc.dictDescription)
		fileTex = []
		fileTex = re.sub('\.[a-z]*', '', elem)
		fileTex = '.'.join([fileTex, 'tex'])
		tex = TexWriter(fileTex, bom.data, dsc.dictDescription)
		tex.write_file()

if __name__ == "__main__":
	main(sys.argv[1:])
