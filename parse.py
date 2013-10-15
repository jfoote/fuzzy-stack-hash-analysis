#!/usr/bin/env python

# Parses bugs.csv and prints FPR to stdout. Quick-and-dirty.
#
# written by jmfoote@andrew.cmu.edu

def parse(csv):
     bugs = 0
     reports = 0
     for line in csv.readlines():
         try:
             reports += int(line.split(",")[-2])
         except Exception as e:
             print "error parsing line %s" % line
             continue
         bugs += 1
     print "%d bugs, %d reports (%f FPR)" % (bugs, reports, 
         1-float(bugs)/float(reports))

import sys
parse(file(sys.argv[1], "rt"))
