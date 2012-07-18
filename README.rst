Linux process swapper
=====================

Simple GTK+ program to start, stop and terminate processes.

In Linux, paused process are swapped firstly, so memory aggressive
programs can be "hibernated" to Linux Swap and release RAM for other
programs.

-----
Usage
-----
Pass path to program as command line parameter or open using graphical dialog.

For example, to swap firefox:
	python swap.py firefox http://www.google.com
And then press Stop


-----
Futures and known bugs
-----
+ Recursive start, stop
+ BUG: termination can be "hard close" or not work at all
