#!/usr/bin/python

# Autograder - since SV is an HDL, the "easiest" way to manange problem
# scores is to print lines to STDOUT and parse printed lines with python.
#
# Command format - #![keyname, value]
#   if value is a number, set keyname equal to value, creating key if needed
#   if value is +=/-=/*=<num> increment/decrement/multiply keyname by <num>
#   if value is ++/--, increment/decrement keyname by <num>
#   if value is rm, the value is removed.
#
# Print format - #$<Message> (prints Message)
#
# After python script recieved EOF, it outputs Autolab's JSON line of:
# { "scores": {"key0":value0, "key1":value1, ...} }

import re

def main():
    values = dict();
    while(True): # Get input from testbench
        try:
            line = raw_input(); # line from testbench
        except EOFError:
            break;
        # put all parsing into one function
        if (line.startswith("#!")): # update dictionary
            values = parseVal(values, line);
        elif (line.startswith("#$")): # command to print
            print(line[2:]);
    printAutoLabStr(values);
    return 0;

# Prints the JSON string that autolab expects at the end of autoGraders
#   valueDict - dictionary of problem name-score pairs
def printAutoLabStr(valueDict):
    autoLabStr = '{ "scores": {';
    for key in valueDict: # keys should all be strings
        value = valueDict[key];
        autoLabStr += '"%s":%s, ' % (key, str(value));
    autoLabStr = autoLabStr[0:-2]; # strip (, ) from end
    autoLabStr += '} }';
    print(autoLabStr);

# Parses a command line (line starting with #!)
#   valueDict - dictionary of problem name-score pairs
#   line - line to parse
#   returns valueDict, updated after command was processed
def parseVal(valueDict, line):
    REGEX = """\#!\[ # match starting she-bang plus first bracket
            (\S+) # matches >= 1 non-whitespace chars (groups()[0])
            , # matches comma
            \s* # matches >= 0 whitespace
            (\S+) # matches >= 1 non-whitespace chars (groups()[1])
            \] # match final bracket""";
    lineMatch = re.match(REGEX, line, re.VERBOSE);
    if (lineMatch == None):
        die("Failed to process line:\n%s" % (line));
    (key, value) = lineMatch.groups();
    if (key not in valueDict and value.isdigit()):
        valueDict[key] = int(value);
    elif (key not in valueDict):
        die("Key not found - must be initalized with an integer")
    else:
        if (value == "++"):
            valueDict[key] += 1;
        elif (value == "--"):
            valueDict[key] -= 1;
        elif (value.startswith("+=")): #must be in form +=<num>; no spaces
             valueDict[key] += int(value[2:]);
        elif (value.startswith("-=")):
            valueDict[key] -= int(value[2:]);
        elif (value.startswith("*=")):
            valueDict[key] *= int(value[2:]);
        elif (value == "rm"):
            del valueDict[key];
        elif (value.isdigit()):
            valueDict[key] = int(value);
        else:
            if (match("[\+\-*]=\s+\d+")):
                die("Command must be in form +=<num>. No spaces.")
            die("Invalid command: %s" % (value));
    return valueDict;

def die(errStr):
    print(errStr);
    exit();

main();
