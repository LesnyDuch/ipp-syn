#!/usr/bin/python3
#
#SYN:xorsza00

import sys
import string
import re
import argparse
from operator import itemgetter

html_codes = ["italic","bold","underline","teletype"]

def format_error():
	sys.exit(4)

# Funkcia na nacitanie formatovacieho suboru
def load_format(filename):

	if (filename == None):
		return None

	lines = []
	try:
		#otvorenie suboru
		file = open(filename, "r")

	except IOError:
		return None

	# Nacitavam subor po riadkoch a spracovavam ich
	with file as f:
		lines = f.readlines()


	for index in range(len(lines)):
		# Oddelim od seba odtabovane celky
		lines[index] = re.sub(r"\t+", "\t",lines[index])
		lines[index] = lines[index].split('\t',1);

		# Z formatovej casti odstranim whitespaces a rozdelim ju podla ciarky
		lines[index][1] = re.sub(r"\s", "", lines[index][1])
		tmp = lines[index][1].split(',')

		for jndex in range(len(tmp)):
			lines[index].append(tmp[jndex])

		lines[index].pop(1);

	# Zatvorenie suboru
	try:
		file.close()
	except IOError:
		print ("Error closing format file")

	return lines

# Kontrola validity formatovacich prikazov
def check_html_validity(form):

	for f in form:
		for index in range(1,len(f)):

			# Ak sa dany prikaz nenachadza medzi validnymi, je bud nespravny, alebo size/color,
			# tie sa kontroluju osobitne

			if (not(f[index] in html_codes)):

				tmp = f[index]
				tmp = tmp.split(":")

				if(len(tmp) != 2):
					format_error()


				# Kontrola color
				if (tmp[0] == "color"):
					# Kontrola, ci hodnota obsahuje validne hex znaky
					if (all(c in string.hexdigits for c in tmp[1])):
						#Kontrola rozsahu hodnoty
						if ((len(tmp[1]) < 1) or (len(tmp[1]) > 6)):
							format_error()

					else:
						format_error()

				# Kontrola size
				elif (tmp[0] == "size"):
					# Kontrola, ci to je validne cislo
					if ((int(tmp[1]) < 1) or (int(tmp[1]) > 7)):
						# print("xxxxx	")
						sys.exit(4)

				else:
					format_error()

# Konvertovanie vstupnych regularnych vyrazov
def convert_regex(form):
	for index in range(len(form)):
		if (re.match(r"[^%]{0,1}\.{2,}", form[index][0]) != None):
			format_error()


		form[index][0] = re.sub(r"(\\n)","\\\\n",form[index][0])
		form[index][0] = form[index][0].replace("\\n","\\\\n")
		form[index][0] = re.sub(r"(\\t)","\\\\t",form[index][0])
		form[index][0] = form[index][0].replace("\\w","\\\\w")
		form[index][0] = form[index][0].replace("\\W","\\\\W")
		form[index][0] = form[index][0].replace("\\s","\\\\s")
		form[index][0] = form[index][0].replace("\\S","\\\\S")
		form[index][0] = form[index][0].replace("\\d","\\\\d")
		form[index][0] = form[index][0].replace("\\D","\\\\D")
		form[index][0] = form[index][0].replace("\\t","\\\\t")
		form[index][0] = re.sub(r"(\?)","\\?",form[index][0])
		form[index][0] = re.sub(r"(\})","\\}",form[index][0])
		form[index][0] = re.sub(r"(\{)","\\{",form[index][0])
		form[index][0] = re.sub(r"(\^)","\\^",form[index][0])
		form[index][0] = re.sub(r"(\])","\\]",form[index][0])
		form[index][0] = re.sub(r"(\[)","\\[",form[index][0])
		form[index][0] = re.sub(r"(\$)","\\$",form[index][0])

		# Najprv upravim %% na %, aby mi nevznikali konflikty
		form[index][0] = form[index][0].replace("%%", "%")

		form[index][0] = form[index][0].replace("%!","!")


		# Odstranenie .
		form[index][0] = re.sub(r"([^%])\.","\g<1>",form[index][0])


		# Lubovolny znak, najprv odstranim !%a, kedze by bol nekompatibilny
		form[index][0] = form[index][0].replace("!%a", "")
		form[index][0] = form[index][0].replace("%a", "[\w\W]")

		# Vykricnik (?:!)\\{0,1}[^%\+\*!\(\)]
		form[index][0] = re.sub(r"!(%{0,1}[^%\+\*!\(\)])","[^\g<1>]",form[index][0])
		form[index][0] = re.sub(r"!(\(.*\))","[^\g<1>]",form[index][0])

		# Whitespace
		form[index][0] = form[index][0].replace("%s","\s")

		# Digit
		form[index][0] = form[index][0].replace("%d","\d")

		# %l
		form[index][0] = form[index][0].replace("%l","[a-z]")
		# %L
		form[index][0] = form[index][0].replace("%L","[A-Z]")
		# %w
		form[index][0] = form[index][0].replace("%w","[a-zA-Z]")
		# %W
		form[index][0] = form[index][0].replace("%W","[a-zA-Z0-9]")

		#Specialne znaky
		form[index][0] = form[index][0].replace("%t","\t")
		form[index][0] = form[index][0].replace("%n","\n")
		form[index][0] = form[index][0].replace("%.","\.")
		form[index][0] = form[index][0].replace("%|","\|")
		form[index][0] = form[index][0].replace("%*","\*")
		form[index][0] = form[index][0].replace("%+","\+")
		form[index][0] = form[index][0].replace("%(","\(")
		form[index][0] = form[index][0].replace("%)","\)")

	return form

# Preformatovanie povodneho textu
def format_input(input_string,form):

	# Tabulka, ktora zachovava, co kam strcit vo formate string tag|index
	table = []
	# Prechadzam pravidla po riadkoch
	for f in form:
		# Kontrola validity regularneho vyrazu
		try:
			regex = re.compile(f[0])

		except re.error:
			sys.exit(1)

		# Najdem vyskyty danych retazcov
		matches = [[match.start(),match.end()] for match in re.finditer(regex,input_string)]

		# Prejdem formatovacie prikazy
		for index in range(1, len(f)):
			table.insert(len(table)+1, [f[index],matches])

	matches = table
	table = []

	for m in matches:

		if (m[0] == "bold"):
			start_tag = "<b>"
			end_tag = "</b>"
		elif (m[0] == "italic"):
			start_tag = "<i>"
			end_tag = "</i>"
		elif (m[0] == "underline"):
			start_tag = "<u>"
			end_tag = "</u>"
		elif (m[0] == "teletype"):
			start_tag = "<tt>"
			end_tag = "</tt>"
		elif (m[0].split(":")[0] == "size"):
			start_tag = "<font size=" + str(m[0].split(":")[1]) + ">"
			end_tag = "</font>"
		elif (m[0].split(":")[0] == "color"):
			start_tag = "<font color=#" + str(m[0].split(":")[1]) + ">"
			end_tag = "</font>"

		for n in range(len(m[1])):
			if (m[1][n][0] != m[1][n][1]):
				table.insert(len(table)+1,[start_tag,m[1][n][0]])

				inserted = False
				for index in range(len(table)):
					if (table[index][1] == m[1][n][1]):
						inserted = True
						table.insert(index,[end_tag,m[1][n][1]])
						break

				if (inserted == False):
					table.insert(len(table)+1,[end_tag,m[1][n][1]])


	table = sorted(table, key = itemgetter(1))

	for i in range(len(table)):
		size = len(table[i][0])
		for j in range(i+1,len(table)):
			table[j][1] +=size

	return(table)


def main():

	parser = argparse.ArgumentParser()
	parser.add_argument("--format", help = "Cesta k formatovaciemu suboru")
	parser.add_argument("--input", help = "Cesta ku vstupnemu suboru")
	parser.add_argument("--output", help = "Cesta ku vystupnemu suboru")
	parser.add_argument("--br", action = 'store_true', help = "Pridanie tagu </ br> na koniec kazdeho riadku vystupneho suboru")

	try:
		args = parser.parse_args()
	except SystemExit:
		sys.exit(1)

	if (args.input != None):

		try:
			#otvorenie suboru
			file = open(args.input, "r")
			input_string = file.read()
			file.close()

		except IOError:
			sys.exit(2)
	else:
		input_string = sys.stdin.read()


	form = load_format(args.format)
	if (form == None):

		output_string = input_string

	else:
		if (form == []):
			output_string = input_string

		else:
			check_html_validity(form)
			form = convert_regex(form)
			form = format_input(input_string,form);

			# Aplikovanie formatovania na string
			form = sorted(form, key = itemgetter(1))

			for t in form:
				input_string = input_string[:int(t[1])] + t[0] + input_string[int(t[1]):]
			output_string = input_string

	if (args.br == True):
		output_string = output_string.replace("\n","<br />\n")

	if (args.output == None):
		print(output_string)

	else:
		try:

			file = open(args.output, "w")
			file.write(output_string)
			file.close()

		except IOError:

			sys.exit(3)

if __name__ == "__main__":
    main()
