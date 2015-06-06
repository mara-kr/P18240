from optparse import OptionParser
from getpass import getuser
from datetime import datetime
from sys import argv

transcript = "" # transcript of every line printed
#global variables
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
}

# we need to do a reverse lookup of the bits in IR when figuring out
# what control state to go into when in the DECODE state
uinst_bin_keys = {v: k for k, v in uinst_str_keys.items()}

# hash: keys are addresses in canonical hex format (uppercase 4 digit)
memory = {}

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
}

# keys are label strings, values are addresses
labels = {}

# keys are addresses, value is always 1
breakpoints = {}

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
}

main();
########################
# Main Subroutine 
########################

def main():
   parser = OptionParser()
   parser.add_option("-v", "--version", action = "store_true", 
                     dest = "get_version", default = False)
   parser.add_option("-r", "--run", action = "store_true",
                     dest = "run_only", default = False)
   parser.add_option("-m", "--memory", action = "store_true",
                     dest = "randomize_memory", default = False)
   parser.add_option("-s", "--seed", action = "store", type = "int"
                     dest = "seed", default = 0)

   (options, args) = parser.parse_args()
   if (options.get_version):
      print("version: " + str(version))
      exit()

   user = getuser()
   date = datetime.now()

   if (seed == 0):
      #not strictly the same as perl, but we just need a default pseduo-rand seed
      seed = str(date.second) + str(date.minute)

   tran("User: " + user)
   tran("Date: " + date.strftime("%a %b %d %Y %I:%M:%S%p"))
   tran("Arguments: " + str(args))
   tran("Seed: " + seed)

   if (len(argv) < 2):
      usage()


def usage():
   line = "./sim240 [list_file] [sim_file]"
   tran(line)
   print(line + "\n")
   exit()

# adds a new line to the transcript - line doesn't include \n
def tran(line):
   transcript += (line + "\n")

