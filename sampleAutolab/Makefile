all:
	vcs -q -sverilog ssd.sv ssd_top.sv
	./simv -q | python autograder.py
