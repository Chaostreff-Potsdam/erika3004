#! /usr/bin/python3
from erika.erika import JustifiedErika
from sys import stdin
import time

e = JustifiedErika("/dev/ttyAMA0")

par = """Heute war der Future SOC Lab Day am HPI |1|. Leider habe ich
den Anfang ab 9:15 Uhr verschlafen, ich dachte, es ginge wie
auf,  dass  ich  am 11 Uhr Meeting teilnehmen kann, aber das
und nicht zwei Matratzen auf dem Boden liegen. :|""".replace("  ", " ").replace("  ", " ")

with e:
    for line in par.split("\n"):
        e.print_stretched_line(line, 60)
        e.print_string("\n")
        e.connection.flush()
        time.sleep(1)
