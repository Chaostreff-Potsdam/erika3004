#! /usr/bin/python3
from erika.erika import Erika
from sys import stdin
import time
e = Erika("/dev/ttyAMA0")
with e:
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
	e.connection.flush()
	time.sleep(1)
