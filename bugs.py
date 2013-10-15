#! /usr/bin/env python

# Quick-and-dirty script to iterate over all projects in projects.txt and 
# output Apport-reported crash reports to bugs.csv.
#
# written by jmfoote@andrew.cmu.edu

import time, sys

from launchpadlib.launchpad import Launchpad

def has_stack_trace(bug):
    '''
    Returns True if this bug report has an Apport-style stack trace attachment.
    Returns False otherwise.
    '''
    for attachment in bug.attachments:
        if attachment.title == "Stacktrace.txt":
            return True
    return False

launchpad = Launchpad.login_anonymously('hello-world', 'production')

bfile = file("bugs.csv", "at")
project_names = file("projects.txt", "rt").read().split("\n")

total_projects = len(project_names)
i = 0
start_time = time.time()

# iterate over all projects and log Apport crash bug report info
for project_name in project_names:
    try:
        print project_name
        pillar = launchpad.projects[project_name]
        
        bugs = pillar.searchTasks(status=["Fix Committed", "Fix Released"])
        # ^ note: omit_duplicates is set to True by default
        for bug in bugs:
    
            # verify bug report was produced by Apport, w/ stack trace 
            if not "crashed with" in bug.title.lower():
                continue
            bug_id_str = str(bug).split("/")[-1]
            bug = launchpad.bugs[bug_id_str]
            if not has_stack_trace(bug):
                continue
    
            # collect duplication info for bug
            count = 1
            if getattr(bug, "number_of_duplicates", False):
                count += bug.number_of_duplicates
            if bug.duplicate_of:
                dupe_of = str(bug.duplicate_of).split("/")[-1]
            else:
                dupe_of = "None"
    
            # log bug to csv file
            bfile.write(",".join([str(pillar).split("/")[-1], str(pillar), 
                bug_id_str, str(bug), str(len(bugs)), str(count), dupe_of]) + "\n")
        i += 1
        print "%d/%d, %f sec remaining" % (i, total_projects, 
            (time.time()-start_time)/i * (total_projects-i))
        sys.stdout.flush()
    except Exception as e:
        print "%s: %s" % (project_name, str(e))
print "done"
