from subprocess import check_output;
sim_name = "python_sim240.py";
test_files = ["gcd", "fibo", "powers", "testRest"];
for fname in test_files:
	list_name = fname + "/" + fname + ".list";
	state_name = fname + "/" + fname + ".state";
	out = check_output(["python", sim_name, list_name, "-g", state_name]);
	if (len(out) > 0):
		print(fname + "failed");
		print(out);
		exit();
	print("Done testing " + fname);
print("Tests sucessful.")