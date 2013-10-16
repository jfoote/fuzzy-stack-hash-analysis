lookat-fsh
==========

A repository for some scripts used to analyze the efficacy of fuzzy stack hashing

TL;DR
----
Using a Ubuntu's Apport crash reporter and Launchpad bug database as a case study, I've found that about 10.66% of bug reports triaged by fuzzy stack hashing correspond to unique bugs (with some assumptions). So, if my assumptions hold, we can say that 89.34% of the time that this type of fuzzy stack hashing said a bug is unique, it was actually wrong (or say it had a 89.34% false-positive rate).

Fuzzy stack hashing
----

[Fuzzy stack hashing](https://www.usenix.org/legacy/event/sec09/tech/full_papers/molnar.pdf) is a common method for making a first-pass at determining whether an application error is unique. For example a program might crash with a SIGSEGV (segmentation fault) signal repeatably when run with some fixed input. An automated tool, such as a crash reporter or debugger plugin, might then triage the bug by hashing (or concatentating) the function signatures (or addresses) of the innermost N frames on the stack. Any subsequent crashes that match this hash (or "signature") are considered to be duplicates and filtered out, so that the human analyst has fewer crash reports to sift through.

For better or worse, bug hunting tools and techniques are sometimes graded by the number of unique crashes they find using a fuzzy stack hash. There is a good discussion in the [comments section](http://blog.regehr.org/archives/1042#comments) of one of John Regher's blog posts on this topic. My comment in that conversation was what motivated me to finally take a first stab at this. Anyway, folks seem to agree that counting "unique" crashes is not necessarily the best way to grade a bug hunting technique. In the small, from a security standpoint, the number of exploits that can be manually generated from the results of the tool or technique are obiviously of more interest. If automated exploit generation is an option, this metric can be scaled cheaply. Even without automatic exploit generation, tagging crashes with an [exploitability heuristic](https://github.com/jfoote/exploitable) (and seeing how many "home runs" your tool produces) may be a better approach. From a completeness standpoint, branch coverage is probably a better metric. Regardless, the fuzzy stack hash is still a commonly automated first pass at determining if a bug is unique.

It is common knowledge that the fuzzy stack hash is not a perfect method for determining if a crash or stack trace represents a unique bug. This blog post reflects some work in trying to determine how good (or bad) fuzzy stack hashing is in the wild.

Taking a stab at determining how effective fuzzy stack hashing is
----

As mentioned above, fuzzy stack hashes are used in other places besides bug hunting tools. Of particular interest are operating system crash reporting tools like ABRT (Red Hat), Windows Error Reporting (Windows), Apport (Ubuntu), and so on. Like bug hunting tools, OS crash reporting tools generally do some sort of stack-based signature generation using a fixed number of the innermost stack frames, which seems to fit Molnar's definition of fuzzy stack hashing. The cool thing about OS crash reporting is that eventually a human manually triages cases where the stack-based signature de-duplication fails. For open source projects, this the results of manual triaging are generally publicly available. Maybe we can learn something about fuzzy stack hashing from the labors of these human triagers.

Apport, and how it works
----

Apport is the crash reporting tool included with Ubuntu Linux. Since Ubuntu 12.04 (and perhaps earlier), [Apport has been included as part of the ErrorTracker system](https://wiki.ubuntu.com/Apport#Ubuntu_12.04_and_later). When a user program triggers an error (like a crash) on an Ubuntu client system, Apport generates a crash signature by concatenating the executable path, signal number, and 5 innermost functions on the stack. If symbols aren't available, Apport uses addresses on the stack in place of function names. Note that in the latter case, Apport may be susceptible to creating large number of duplicates if the stack is corrupted during the crash, etc. As a mitigation for this and other weaknesses to address-only signatures, the system does some client-side de-duplication of crashes so that only a single report is submitted in these cases. (for more info on this I recommend reading the Apport source, using apport/report.py::crash\_signature as a starting point)

Once a crash report is generated on a client system it is sent to a retrace server, which de-duplicates crashes across client reports based on the crash signature included in the report, respectively, generates a stack trace with debug symbols, and forwards the result on to human Ubuntu triagers to move the bug through Launchpad (Launchpad includes Ubuntu's bug triaging system, among other things). ([src](https://wiki.ubuntu.com/Bugs/ApportRetraces)).

Finding Apport-reported crashes in Launchpad
----

When Apport reports a bug that includes a stack trace, the trace is included as an attachment on the report named "Stacktrace.txt". In addition, if we look at apport/report.py::standard\_title (around line 1084 in apport-2.92), we can see that the bug report title will be "(app info) crashed with (signal info)" if the report is the result of the crash. Using these two heuristics, we can search Launchpad for crashes report by Apport, which uses fuzzy-stack-hash-style crash signatures, and learn about how many duplicates are generated.

Here is how I parsed the data:
----
1. Due to known issues in the Launchpad API, I was unable to iterate over all of the projects in Launchpad using a single iterator (eventually, an exception is raised). So I wrote a very quick-and-dirty scraper to get all of the project names from the Launchpad website into a text file. You can find that [here](https://github.com/jfoote/lookat-fsh/blob/master/scrape_project_names.py)

2. The next step is to read in the project names and iterate over the bug reports for each, looking for Apport-reported crashes, counting duplicates, etc. You can find a script that does this (and outputs results to a CSV file) [here](https://github.com/jfoote/lookat-fsh/blob/master/bugs.py).

3. Finally, I wrote a quick [script](https://github.com/jfoote/lookat-fsh/blob/master/parse.py) to calculate the FPR based on the contents of the CSV file.

Assumptions and conclusion
----

All of the above steps were carried out on a t1.micro Ubuntu Amazon EC2 instance. There is one issue I wasn't able to nail down here: because most of the duplicate bug reports have been deleted, I can't run the heuristic against the duplicate reports to verify that they were generated by Apport. It seems reasonable to assume that most of the dupe bugs were produced by Apport, but I'd really like to check this. I asked [a question](https://answers.launchpad.net/apport/+question/236701) about this back when I wrote these scripts but I haven't heard anything yet. Ideally I'd be able to access historical Launchpad data and run the heuristics against duplicate bugs as well to verify my assumption. If one was motivated though, they could monitor the Launchpad DB on a daily or weekly basis for a few months to capture duplicate reports before they were deleted.

When I ran these scripts a few weeks ago I found 32,843 projects in Launchapd with 19,530 Apport-reported crash reports corresponding to 2081 bugs. This gives us a 89.34% FPR. I had plans to do more analysis (per-project, etc.) but I haven't made any progress in a while, so I figured I'd publish what I had. If you have any questions/comments feel free to drop me a line.

Thanks for reading.
