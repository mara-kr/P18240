from optparse import OptionParser
from getpass import getuser
from datetime import datetime
from sys import argv
from re import match
from random import randint
# Globals
version = "1.21py"

user = ""; # holds user name from $USER environment var
date = ""; # holds date and time info

transcript = ""; # holds transcript of every line printed
seed = ""; # seed used for random memory

randomize_memory = False; # flag that randomizes the memory
run_only = False; # flag that just does "run, quit"

wide_header = "Cycle STATE PC   IR   SP   ZNCV MAR  MDR  R0   R1   R2   R3   R4   R5   R6   R7\n";

# print_per is a variable which determines when the simulator prints the state
# to the console.
# 'i' prints the state on every instruction. '
# 'u' prints the state on every microinstruction. '
# 'q' is for 'quiet'; it does not ever print
print_per = "i";

cycle = 0; # global cycle counter

# a hash of microinstruction binary opcodes
uinst_str_keys = {
# Microcode operations (i.e., FSM states)
   'FETCH'  : '00_0000_0000',
   'FETCH1' : '00_0000_0001',
   'FETCH2' : '00_0000_0010',
   'DECODE' : '00_0000_0100',
   'STOP'   : '00_1100_0000',
   'STOP1'  : '00_1100_0001',

# Load operations: MOV, LDA, LDR, LDI
   'MOV'    : '00_1110_1000',
   'LDA'    : '00_0001_0000',
   'LDA1'   : '00_0001_0001',
   'LDA2'   : '00_0001_0010',
   'LDA3'   : '00_0001_0011',
   'LDA4'   : '00_0001_0100',
   'LDR'    : '00_0010_0000',
   'LDR1'   : '00_0010_0001',
   'LDR2'   : '00_0010_0010',
   'LDI'    : '00_0011_0000',
   'LDI1'   : '00_0011_0001',
   'LDI2'   : '00_0011_0010',

# Store operations: STA, STR
   'STA'    : '00_0001_1000',
   'STA1'   : '00_0001_1001',
   'STA2'   : '00_0001_1010',
   'STA3'   : '00_0001_1011',
   'STA4'   : '00_0001_1100',
   'STR'    : '00_0010_1000',
   'STR1'   : '00_0010_1001',
   'STR2'   : '00_0010_1010',

# Branch operations: BRA, BRN, BRZ, BRC, BRV
   'BRA'    : '00_1010_0000',
   'BRA1'   : '00_1010_0001',
   'BRA2'   : '00_1010_0010',
   'BRN'    : '00_1011_0000',
   'BRN1'   : '00_1011_0001',
   'BRN2'   : '00_1011_0010',
   'BRN3'   : '00_1011_0011',
   'BRZ'    : '00_1010_1000',
   'BRZ1'   : '00_1010_1001',
   'BRZ2'   : '00_1010_1010',
   'BRZ3'   : '00_1010_1011',
   'BRC'    : '01_0010_0000',
   'BRC1'   : '01_0010_0001',
   'BRC2'   : '01_0010_0010',
   'BRC3'   : '01_0010_0011',
   'BRV'    : '00_1011_1000',
   'BRV1'   : '00_1011_1001',
   'BRV2'   : '00_1011_1010',
   'BRV3'   : '00_1011_1011',

# Arithmetic operations: ADD, SUB, INCR, DECR, NEG
   'ADD'    : '00_0011_1000',
   'SUB'    : '00_0100_0000',
   'INCR'   : '00_0101_0000',
   'DECR'   : '00_0101_1000',
   'NEG'    : '00_0100_1000',
   'NEG1'   : '00_0100_1001',
 
# Logical operations: AND, NOT, OR, XOR
   'AND'    : '00_0110_1000',
   'NOT'    : '00_0110_0000',
   'OR'     : '00_0111_0000',
   'XOR'    : '00_0111_1000',

# Comparison operations: CMI, CMR
   'CMI'    : '01_0001_0000',
   'CMI1'   : '01_0001_0001',
   'CMI2'   : '01_0001_0010',
   'CMR'    : '01_0001_1000',

# Shift operations: ASHR, LSHL, LSHR, ROL
   'ASHR'   : '00_1001_1000',
   'LSHL'   : '00_1000_0000',
   'LSHR'   : '00_1001_0000',
   'ROL'    : '00_1000_1000',

# Stack operations: JSR, LDSF, LDSP, POP, PUSH, RTN, STSF, STSP, ADDSP
   'JSR'    : '00_1101_1000',
   'JSR1'   : '00_1101_1001',
   'JSR2'   : '00_1101_1010',
   'JSR3'   : '00_1101_1011',
   'JSR4'   : '00_1101_1100',
   'JSR5'   : '00_1101_1101',
   'LDSF'   : '01_0000_0000',
   'LDSF1'  : '01_0000_0001',
   'LDSF2'  : '01_0000_0010',
   'LDSF3'  : '01_0000_0011',
   'LDSF4'  : '01_0000_0100',
   'LDSP'   : '00_1111_0000',
   'POP'    : '00_1101_0000',
   'POP1'   : '00_1101_0001',
   'POP2'   : '00_1101_0010',
   'PUSH'   : '00_1100_1000',
   'PUSH1'  : '00_1100_1001',
   'PUSH2'  : '00_1100_1010',
   'RTN'    : '00_1110_0000',
   'RTN1'   : '00_1110_0001',
   'RTN2'   : '00_1110_0010',
   'STSF'   : '01_0000_1000',
   'STSF1'  : '01_0000_1001',
   'STSF2'  : '01_0000_1010',
   'STSF3'  : '01_0000_1011',
   'STSF4'  : '01_0000_1100',
   'STSP'   : '00_1111_1000',
   'ADDSP'  : '00_0011_1100',
   'ADDSP1' : '00_0011_1101',
   'ADDSP2' : '00_0011_1110',
#   UNDEF   : xx_xxxx_xxxx # NOTE: needed?
};

# we need to do a reverse lookup of the bits in IR when figuring out
# what control state to go into when in the DECODE state
uinst_bin_keys = {v: k for k, v in uinst_str_keys.items()};

# hash: keys are addresses in canonical hex format (uppercase 4 digit)
memory = {};

# all the regs in the processor
state = {
   'PC' : '0000',
   'SP' : '0000',
   'IR' : '0000',
   'MAR' : '0000',
   'MDR' : '0000',
   'regFile' : ['0000',
                '0000',
                '0000',
                '0000',
                '0000',
                '0000',
                '0000',
                '0000'],
   'Z' : '0',
   'N' : '0',
   'C' : '0',
   'V' : '0',
   'STATE' : 'FETCH',
};

# keys are label strings, values are addresses
labels = {};

# keys are addresses, value is always 1
breakpoints = {};

# keys are strings indicating menu option
# values are regex's which match the input for the corresponding menu option
menu = {
   'quit'    : '^\s*(q(uit)?|exit)\s*$',
   'help'    : '^\s*(\?|h(elp)?)\s*$',                         # ? ; h ; help
   'reset'   : '^\s*reset\s*$',
   'run'     : '^\s*r(un)?\s*(\d*)?\s*([qiu])?\s*$',           # run ; run 5u ; r 6i
   'step'    : '^\s*s(tep)?$',                                 # s ; step
   'ustep'   : '^\s*u(step)?\s*$',                             # u ; ustep
   'break'   : '^\s*break\s+(\'?\w+\'?|[0-9a-f]{1,4})\s*$',    # break [addr/label]
   'clear'   : '^\s*clear\s+(\*|\'?\w+\'?|[0-9a-f]{1,4})\s*$', # clear [addr/label/*]
   'lsbrk'   : '^\s*lsbrk\s*$',
   'load'    : '^\s*load\s+([\w\.]+)\s*$',                     # load [file]
   'save'    : '^\s*save\s+([\w\.]+)\s*$',                     # save [file]
   'set_reg' : '^\s*(\*|pc|sp|ir|mar|mdr|z|c|v|n|r[0-7])\s*=\s*([0-9a-f]{1,4})$',
   'get_reg' : '^\s*(\*|pc|sp|ir|mar|mdr|z|c|v|n|state|r[0-7*])\s*\?$',
   'set_mem' : '^\s*m(em)?\[([0-9a-f]{1,4})\]\s*=\s*([0-9a-f]{1,4})$',   # m[10] = 0a10
   'get_mem' : '^\s*m(em)?\[([0-9a-f]{1,4})(:([0-9a-f]{1,4}))?\]\s*\?$', # m[50]? ; mem[10:20]?
   'print'   : '^\s*print\s*$',
};

# filehandles
list_fh = None;
sim_fh = None;
list_lines = [];

main();
########################
# Main Subroutine 
########################

def main():
   parser = OptionParser();
   parser.add_option("-v", "--version", action = "store_true", 
                     dest = "get_version", default = False);
   parser.add_option("-r", "--run", action = "store_true",
                     dest = "run_only", default = False);
   parser.add_option("-m", "--memory", action = "store_true",
                     dest = "randomize_memory", default = False);
   parser.add_option("-s", "--seed", action = "store", type = "int"
                     dest = "seed", default = 0);

   (options, args) = parser.parse_args();
   if (options.get_version):
      print("version: " + str(version));
      exit();

   global run_only;
   run_only = options.run_only;

   global randomize_memory;
   randomize_memory = options.randomize_memory;

   global user;
   global date;
   user = getuser();
   date = datetime.now();

   global seed;
   seed = options.seed;
   if (seed == 0):
      #not strictly the same as perl, but we just need a default pseduo-rand seed
      seed = str(date.second) + str(date.minute);

   tran("User: " + user);
   tran("Date: " + date.strftime("%a %b %d %Y %I:%M:%S%p"));
   tran("Arguments: " + str(args));
   tran("Seed: " + seed);

   if (len(args) < 1): #args takes out flags and argv[0]
      usage();

   list_filename = args[0];
   global sim_fh;
    # sim file is optional (read input from STDIN if not specified)
   if (len(args) > 1):
      sim_filename = args[1];
      try:
         sim_fh = open(sim_filename, "r");
      except:
         print("Failed to open sim_file\n");
         exit();
   
   global list_fh;
   try:
      list_fh = open(list_filename, "r");
   except:
      print("Failed to open list_file");
      exit();
   
   # read all lines from list_fh, store in array, remove first 2 lines
   global list_lines;
   list_lines = list_fh.readlines();
   list_lines.pop(0); # remove 'addr data  label   opcode  operands'
   list_lines.pop(0); # remove '---- ----  -----   ------  --------'

   init();

   interface(sim_fh); #start taking input from user
   save_tran(); #save transcript

   if (sim_fh != None): close(sim_fh);
   close(list_fh);

def init():
   get_labels();

   init_p18240(); #put p18240 into a known state
   init_memory(); #initalize the memory


def usage():
   tran_print("./sim240 [list_file] [sim_file]\n");
   exit();

# Reads label from list file and adds them to the labels hash.
# Currently based on spacing format of list file.
def get_labels():
   #check each line for a label
   global labels;
   for line in list_lines:
      if (len(line) < 11): continue; #must not be a lebel on this line
      addr = line[0:4];
      line_start_at_label = line[11:];
      end_of_label = line_start_at_label.find(' '); #first space (label end)
      label = line_start_at_label[0:end_of_label];
      lables[label] = addr;

# Interface Code
# Loop on user input executing commands until they quit
# Arguments:
#  * file handle for sim file.
# Return value:
#  * None
def interface(input_fh):
   done = False; # flag indicating user is done and wants to quit
   if (input_fh == None):
      taking_user_input = True;
   else:
      taking_user_input = False;

   if (run_only):
      run();
      done = True;

   while (not done):
      tran("> ");
      if (not taking_user_input):
          line = input_fh.readline();
          if (len(line) == 0):
            taking_user_input = True;
            continue;
      else:
         line = raw_input("> ");

      # assume user input is valid until discovered not to be
      valid = True;
      if (match(menu["quit"], line)): 
         done = True;
      elif (match(menu["help"], line)): 
         print_help();
      elif (match(menu["run"], line)):
         matchObj = match(menu["run"], line); #@fix can't assign inside if
         run(matchObj.group(2), matchObj.group(3));
      elif (match(menu["step"], line)):
         if (print_per == "i"): tran_print(wide_header);
         step();
         if (print_per == "i"): print_state();
      elif (match(menu["ustep"], line)):
         if (print_per == "u"): tran_print(wide_header);
         cycle();
         if (print_per == "u"): print_state;
      elif (match(menu["break"], line)):
         matchObj = match(menu["break"], line);
         set_breakpoint(matchObj.group(1));
      elif (match(menu["clear"], line)):
         matchObj = match(menu["clear"], line);
         clear_breakpoint(matchObj.group(1));
      elif (match(menu["lsbrk"], line)):
         list_breakpoints();
      elif (match(menu["load"], line)):
         matchObj = match(menu["load"], line);
         load(matchObj.group(1));
      elif (match(menu["save"], line)):
         matchObj = match(menu["save"], line);
         save(matchObj.group(1));
      elif (match(menu["set_reg"], line)):
         matchObj = match(menu["set_reg"], line);
         set_reg(matchObj.group(1), matchObj.group(2));
      elif (match(menu["get_reg"], line)):
         matchObj = match(menu["get_reg"], line);
         get_reg(matchObj.group(1));
      elif (match(menu["set_mem"], line)):
         matchObj = match(menu["set_mem"], line);
         set_memory(matchObj.group(2), matchObj.group(3));
      elif (match(menu["get_mem"], line)):
         matchObj = match(menu["get_mem"], line);
         fget_memory({"lo" : matchObj.group(2),
                      "hi" : matchObj.group(4)});
      elif (match(menu["print"], line)):
         print_tran_lpr();
      elif (match("^$", line)): # user just struck enter
         pass; # something needs to be here for python
      else:
         valid = False;

      if (not valid):
         tran_print("Invalid input. Type 'help' for help.");

def print_help():
   help_msg = '';
   help_msg += "\n";
   help_msg += "quit,q,exit                Quit the simulator.\n";
   help_msg += "help,h,?                   Print this help message.\n";
   help_msg += "step,s                     Simulate one instruction.\n";
   help_msg += "ustep,u                    Simulate one micro-instruction.\n";
   help_msg += "run,r [n]                  Simulate the next n instructions.\n";
   help_msg += "break [addr/label]         Set a breakpoint for instruction located at [addr] or [label].\n";
   help_msg += "lsbrk                      List all of the breakpoints set.\n";
   help_msg += "clear [addr/label/*]       Clear a breakpoint set for [addr], [label], or clear all.\n";
   help_msg += "reset                      Reset the processor to initial state.\n";
   help_msg += "save [file]                Save the current state to a file.\n";
   help_msg += "load [file]                Load the state from a given file.\n";
   help_msg += "\n";
   help_msg += "You may set registers like so:          PC=100\n";
   help_msg += "You may view register contents like so: PC?\n";
   help_msg += "You may view the register file like so: R*?\n";
   help_msg += "You may view all registers like so:     *?\n";
   help_msg += "\n";
   help_msg += "You may set memory like so:  m[00A0]=100\n";
   help_msg += "You may view memory like so: m[00A0]? or with a range: m[0:A]?\n";
   help_msg += "\n";
   help_msg += "Note: All constants are interpreted as hexadecimal.\n";
   help_msg += "\n";
   tran_print($help_msg);
 

def init_p18240():
   global cycle;
   cycle = 0;

   global state;
   for key in state:
      if (key == "regFile"):
         for i in xrange(8):
            state["regFile"][i];
      elif (match("[ZNCV]", key)):
         state[key] = "0";
      elif (key == "STATE"):
         state[key] = "FETCH";
      else:
         state[key] = "0000";

def init_memory():
   global memory;
   memory = {};
   int_max = (1 << 16) - 1; # 16-bit ints
   global randomize_memory;
   if (randomize_memory):
      for addr in xrange(1 << 16):
         data = randint(0, int_max);
         set_memory(addr, data);

   global list_lines;
   for line in list_lines:
      arr = line.split(" ");
      addr = arr[0];
      data = arr[1];
      memory[addr] = data.lower();

# Run simulator for n instructions
# If n is undefined, run indefinitely
# In either case, the exception is to stop
# at breakpoints or the STOP microinstruction
def run(num, print_per_requested):
   if (not num): num = (1<<32);
   global print_per;
   print_per_tmp = print_per;
   if (print_per_requested): print_per = print_per_requested;
   if (print_per != "q"): tran_print(wide_header);

   for i in xrange(num):
      step();
      if (print_per == "i"): print_state();
      if (state["PC"] in breakpoints):
         tran_print("Hit breakpoint at " + state["PC"] + ".\n");
         break;

      if (state["STATE"] == "STOP1"):
         break;

   print_per = print_per_tmp;

# Simulate one instruction
def step():
   cycle(); # @fix should just be do-while loop, doesn't exist in python
   if (print_per == "u"): print_state();
   while (not match(state["STATE"], "^(STOP1|FETCH)$")):
      cycle():
      if (print_per == "u"): print_state();

# Set a break point at a given address of label.
# Any thing which matches a hex value (e.g. a, 0B, etc) is interpreted
# as such *unless* it is surrounded by '' e.g. 'A' in which case it is
# interpreted as a label and looked up in the labels hash.
# Anything which does not match a hex value is also interpreted as a label
# with or without surrounding ''.
def set_breakpoint(arg):
   is_label = False;
   if (match("^'(\w+)'$", arg)):
      label = match("^'(\w+)'$", arg).group(1);
      is_label = True;
   elif (match("^[0-9a-f]{1,4}$"), arg):
      addr = to_4_digit_uc_hex(arg);
   else:
      is_label = True;
      label = arg;

   if (is_label):
      if (label in labels):
         addr = labels[label];
      else:
         tran_print("Invalid label.");
         return;

   global breakpoints;
   breakpoints[addr] = 1;

def clear_breakpoint(arg):
   clear_all = False;
   is_label = False;

   if (match("^'(\w+)'$", arg)):
      label = match("^'(\w+)'$", arg).group(1);
      is_label = True;
   elif (match("^[0-9a-f]{1,4}$"), arg):
      addr = to_4_digit_uc_hex(arg);
   elif (arg == "*"):
      clear_all = True;
   else:
      label = arg;
      is_label = True;

   if (is_label):
      if (label in lables):
         addr = labels[label];
      else:
         tran_print("Invalid label.");
         return;

   global breakpoints;
   if (clear_all):
      breakpoints = {};
   else:
      if (addr in breakpoints):
         del breakpoints[addr];
      else: #no break point at that address
         if (is_label):
            tran_print("No breakpoint at " + label + ".");
         else:
            tran_print("No breakpoint at " + addr + ".");

# Print out all of the breakpoints and the addresses.
def list_breakpoints():
   for key in breakpoints:
      tran_print(key);

# TODO: load a state file
def load(filename):
   tran_print("Feature not yet available.");

# TODO: finish this subroutine.
# Supposed to save all of the state to a file which can be
# restored using load.
def save(filename):
   tran_print("saving to $file...");
   fh = open(filename, "w");
   fh.write("Seed: " + seed + "\n");
   fh.write("Breakpoints:\n");
   for key in breakpoints:
      fh.write(key + "\n");
   fh.write("State:\n");
   fh.write(get_state());
   fh.write("Memory:\n");
   fget_memory({"fh" : fh,
                "lo" : '0',
                "hi" : "ffff",
                "zeros" : 0});
   close(fh);

def set_reg(reg_name, value):
   global state;
   if (match('^R([0-7])$', reg_name)):
      state["regFile"][match('^R([0-7])$', reg_name).group(1)] = value;
   elif (match("^[ZNCV]$", reg_name)):
      if (match("^[01]$", reg_name)):
         state[reg_name] = value;
      else:
         tran_print("Value must be 0 or 1 for this register.");
   else:
      state[reg_name] = to_4_digit_uc_hex(value);

def get_reg(reg_name):
   if (reg_name == "*"):
      tran_print(get_state());
   elif (reg_name == "R*"):
      print_regfile();
   elif (match("R([0-7])", reg_name)):
      reg_num = match("R([0-7])", reg_name).group(1);
      tran_print("R%d: %s\n" % (reg_num, state["regFile"][reg_num]));
   else:
      value = state[reg_name];
      tran_print("%s: %s\n" % (reg_name, value));

def get_state():
   (Z,N,C,V) = (state["Z"], state["N"], state["C"], state["V"]);
   



# adds a new line to the transcript - line doesn't include \n
def tran(line):
   global transcript;
   transcript += (line);

# add the string to the transcript and print to file
def tran_print(line):
   tran(line + "\n");
   print(line);

