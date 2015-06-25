# Test Suite for sim240. Runs various subroutines, then checks state against
# state from executing the same subroutine on version 1.21. Prints error output
# if state doesn't match.
#
# To Run : set sim_name to whatever the name of the simulator to be tested
# is and move the simulator script to the tests/ folder, then run. See
# the simulator documentation for explanation of '-g' flag.
#
# Written by Neil Ryan <nryan@andrew.cmu.edu>
# Last updated 6/18/2015

from subprocess import check_output;

sim_name = "sim240";
test_files = ["gcd", "fibo", "powers", "testRest"];
for fname in test_files:
	list_name = fname + "/" + fname + ".list";
	state_name = fname + "/" + fname + ".state";
	out = check_output(["python", sim_name, list_name, "-g", state_name,
                            "-r"]);
	if (len(out) > 0):
		print(fname + "failed");
		print(out);
		exit();
	print("Done testing " + fname);
print("Tests sucessful.")
