#!/usr/bin/python

# convert twiki syntax to moinmoin  - only the most important stuff

import re
import sys

t = str(sys.stdin.read())

t = re.sub (r'===== (.*) =====', r'---+++++ \1', t) 
t = re.sub (r'==== (.*) ====', r'---++++ \1', t) 
t = re.sub (r'=== (.*) ===', r'---+++ \1', t) 
t = re.sub (r'== (.*) ==', r'---++ \1', t) 
t = re.sub (r'= (.*) =', r'---+ \1', t) 


t = re.sub (r'\|\|', r'|', t)

t = re.sub (r"'''", r"*", t) 

print t



