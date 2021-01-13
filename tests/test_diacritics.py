#! /usr/bin/python3
from erika.erika import Erika
from sys import stdin
import time
e = Erika("/dev/ttyAMA0")
with e:
	e.print_string("\n")
	e.print_string("Test Single Diacritics")
	e.print_string("\n")
	e.print_string("----------------------")
	e.print_string("\n")
	e.print_string("^^^")
	e.print_string("\n")
	e.print_string("```")
	e.print_string("\n")
	e.print_string("´´´")
	e.print_string("\n")
	e.print_string("¨¨¨")
	e.print_string("\n")
	e.print_string("°°°")
	e.print_string("\n")
	e.print_string("²²²")
	e.print_string("\n")
	e.print_string("³³³")
	e.print_string("\n")

	e.print_string("\n")
	e.print_string("Test Combined Diacritics")
	e.print_string("\n")
	e.print_string("------------------------")
	e.print_string("\n")
	e.print_string("âĉêĝĥîĵôŝûŵŷẑ")
	e.print_string("\n")
	#
	e.print_string("áćéǵíj́ḱĺḿńóṕŕśúǘẃýź")
	e.print_string("\n")
	#
	e.print_string("àèìǹm̀òùǜẁỳ")
	e.print_string("\n")
	e.print_string("äëïöüÿÄËÏÖÜŸ")
	e.print_string("\n")
