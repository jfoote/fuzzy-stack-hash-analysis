#!/usr/bin/env python

# Quick-and-dirty script to scrape project names from Launchpad website. 
# Used as a workaround to issue with Launchpad Python API that prohibits
# looping over all projects via an iterator. Prints results to stdout.
#
# written by jmfoote@andrew.cmu.edu

import re
import requests

batch = 300
total = 32843
for i in range(0, total, batch):
    uri = "https://launchpad.net/projects/+all?batch=%d&memo=%d&start=%d" % (batch, i, i)
    page = requests.get(uri)
    proj_count = 0
    lines = page.text.splitlines()
    projects = []
    for j in range(0, len(lines)):
        m = re.match("^[ ]*<a href=\"/(.*)\" class=\".*$", lines[j])
        if m:
            if j > 1 and "<div>" in lines[j-1]:
                proj_count += 1
                projects.append(m.groups()[0])
    if proj_count!= batch:
        print "hiccup: proj_count=%d, batch=%d, uri=%s" % (proj_count, batch,
            uri)
    print "\n".join(projects)

