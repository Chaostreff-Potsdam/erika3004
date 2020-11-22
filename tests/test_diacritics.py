#! /usr/bin/python3
from erika.erika import Erika
from sys import stdin
import time
e = Erika("/dev/ttyAMA0")
with e:
	# e.print_string("\n")
	# e.print_string("Test Single Diacritics")
	# e.print_string("\n")
	# e.print_string("----------------------")
	# e.print_string("\n")
	# e.print_string("^^^")
	# e.print_string("\n")
	# e.print_string("```")
	# e.print_string("\n")
	# e.print_string("´´´")
	# e.print_string("\n")
	# e.print_string("¨¨¨")
	# e.print_string("\n")
	# e.print_string("°°°")
	# e.print_string("\n")
	# e.print_string("²²²")
	# e.print_string("\n")
	# e.print_string("³³³")
	# e.print_string("\n")

	e.print_string("\n")
	e.print_string("Test Combined Diacritics")
	e.print_string("\n")
	e.print_string("------------------------")
	e.print_string("\n")
	e.print_string("âĉêĝĥîĵôŝûŵŷẑ")
	e.print_string("\n")
	#j́
	e.print_string("áćéǵíḱĺḿńóṕŕśúǘẃýź")
	e.print_string("\n")
	#j́m̀
	e.print_string("àèìǹòùǜẁỳ")
	e.print_string("\n")
	e.print_string("äëïöüÿÄËÏÖÜŸ")
	e.print_string("\n")
