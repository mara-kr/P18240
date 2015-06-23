#!/usr/bin/env python

# sim240.py: Version 1.3
# Simulator for p18240
# Written by Neil Ryan <nryan@andrew.cmu.edu>
# Adapted from perl script by Paul Kennedy (version 1.21)
# Last updated 6/18/2015
#
# In Progress:
#
# Known Bugs:
# If any additional bugs are found, contact nryan@andrew.cmu.edu
from optparse import OptionParser
from getpass import getuser
from datetime import datetime
import sys
from sys import argv
from re import match
import re
from random import randint
from string import join
import signal
import readline

# supress .pyc file - speedup doesn't justify cleanup
sys.dont_write_bytecode = True; 
# Globals
version = "1.3"

transcript = ""; # holds transcript of every line printed

randomize_memory = False; # flag that randomizes the memory
run_only = False; # flag that just does "run, quit"
create_transcript = False; # flag that creates transcript of events if set
check_file = ""; # file to check state against in grading mode
quit_after_sim_file = False; # if -g is set and a sim file is provided,
                             # we quit after running the sim file

wide_header = "Cycle STATE PC   IR   SP   ZNCV MAR  MDR  R0   R1   R2   R3   R4   R5   R6   R7";

# print_per is a variable which determines when the simulator prints the state
# to the console.
# 'i' prints the state on every instruction. '
# 'u' prints the state on every microinstruction. '
# 'q' is for 'quiet'; it does not ever print
print_per = "i";

cycle_num = 0; # global cycle counter

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
   'check' : '^\s*check\s+([\w\.]+)\s*$', # check [state filename]
};

# filehandles
list_fh = None;
sim_fh = None;

list_lines = [];

# Next state logic based on current state. Empty strings are states 
# dependent on flags
nextState_logic = {
   "FETCH" : ['F_A',        'PC',  'x',    'MAR',   'NO_LOAD',    'NO_RD',    'NO_WR',    'FETCH1'],
   "FETCH1": ['F_A_PLUS_1', 'PC',  'x',    'PC',    'NO_LOAD',    'MEM_RD',   'NO_WR',    'FETCH2'],
   "FETCH2": ['F_A',        'MDR', 'x',    'IR',    'NO_LOAD',    'NO_RD',    'NO_WR',    'DECODE'],
   "DECODE": ['x',          'x',   'x',    'NONE',  'NO_LOAD',    'NO_RD',    'NO_WR',    ""], #IR state
   "LDI"   : ['F_A',        'PC',  'x',    'MAR',   'NO_LOAD',    'NO_RD',    'NO_WR',    'LDI1'],
   "LDI1"  : ['F_A_PLUS_1', 'PC',  'x',    'PC',    'NO_LOAD',    'MEM_RD',   'NO_WR',    'LDI2'],
   "LDI2"  : ['F_A',        'MDR', 'x',    'REG',   'LOAD_CC',    'NO_RD',    'NO_WR',    'FETCH'],
   "ADD"   : ['F_A_PLUS_B', 'REG', 'REG',  'REG',   'LOAD_CC',    'NO_RD',    'NO_WR',    'FETCH'],
   "SUB"   : ['F_A_MINUS_B','REG', 'REG',  'REG',   'LOAD_CC',    'NO_RD',    'NO_WR',    'FETCH'],
   "INCR"  : ['F_A_PLUS_1', 'REG', 'x',    'REG',   'LOAD_CC',    'NO_RD',    'NO_WR',    'FETCH'],
   "DECR"  : ['F_A_MINUS_1','REG', 'x',    'REG',   'LOAD_CC',    'NO_RD',    'NO_WR',    'FETCH'],
   "LDR"   : ['F_B',        'x',   'REG',  'MAR',   'NO_LOAD',    'NO_RD',    'NO_WR',    'LDR1'],
   "LDR1"  : ['x',          'x',   'x',    'NONE',  'NO_LOAD',    'MEM_RD',   'NO_WR',    'LDR2'],
   "LDR2"  : ['F_A',        'MDR', 'x',    'REG',   'LOAD_CC',    'NO_RD',    'NO_WR',    'FETCH'],
   "BRA"   : ['F_A',        'PC',  'x',    'MAR',   'NO_LOAD',    'NO_RD',    'NO_WR',    'BRA1'],
   "BRA1"  : ['x',          'x',   'x',    'NONE',  'NO_LOAD',    'MEM_RD',   'NO_WR',    'BRA2'],
   "BRA2"  : ['F_A',        'MDR', 'x',    'PC',    'NO_LOAD',    'NO_RD',    'NO_WR',    'FETCH'],
   "BRN"   : ['F_A',        'PC',  'x',    'MAR',   'NO_LOAD',    'NO_RD',    'NO_WR',    ""], #BRN_next
   "BRN1"  : ['F_A_PLUS_1', 'PC',  'x',    'PC',    'NO_LOAD',    'NO_RD',    'NO_WR',    'FETCH'],
   "BRN2"  : ['x',          'x',   'x',    'NONE',  'NO_LOAD',    'MEM_RD',   'NO_WR',    'BRN3'],
   "BRN3"  : ['F_A',        'MDR', 'x',    'PC',    'NO_LOAD',    'NO_RD',    'NO_WR',    'FETCH'],
   "BRZ"   : ['F_A',        'PC',  'x',    'MAR',   'NO_LOAD',    'NO_RD',    'NO_WR',    ""], #BRZ_next
   "BRZ1"  : ['F_A_PLUS_1', 'PC',  'x',    'PC',    'NO_LOAD',    'NO_RD',    'NO_WR',    'FETCH'],
   "BRZ2"  : ['x',          'x',   'x',    'NONE',  'NO_LOAD',    'MEM_RD',   'NO_WR',    'BRZ3'],
   "BRZ3"  : ['F_A',        'MDR', 'x',    'PC',    'NO_LOAD',    'NO_RD',    'NO_WR',    'FETCH'],
   "STOP"  : ['F_A_MINUS_1','PC',  'x',    'PC',    'NO_LOAD',    'NO_RD',    'NO_WR',    'STOP1'],
   "STOP1" : ['x',          'x',   'x',    'NONE',  'NO_LOAD',    'NO_RD',    'NO_WR',    'STOP1'], # same as above
   "BRC"   : ['F_A',        'PC',  'x',    'MAR',   'NO_LOAD',    'NO_RD',    'NO_WR',    ""], #BRC_next
   "BRC1"  : ['F_A_PLUS_1', 'PC',  'x',    'PC',    'NO_LOAD',    'NO_RD',    'NO_WR',    'FETCH'],
   "BRC2"  : ['x',          'x',   'x',    'NONE',  'NO_LOAD',    'MEM_RD',   'NO_WR',    'BRC3'],
   "BRC3"  : ['F_A',        'MDR', 'x',    'PC',    'NO_LOAD',    'NO_RD',    'NO_WR',    'FETCH'],
   "BRV"   : ['F_A',        'PC',  'x',    'MAR',   'NO_LOAD',    'NO_RD',    'NO_WR',    ""], #BRV_next
   "BRV1"  : ['F_A_PLUS_1', 'PC',  'x',    'PC',    'NO_LOAD',    'NO_RD',    'NO_WR',    'FETCH'],
   "BRV2"  : ['x',          'x',   'x',    'NONE',  'NO_LOAD',    'MEM_RD',   'NO_WR',    'BRV3'],
   "BRV3"  : ['F_A',        'MDR', 'x',    'PC',    'NO_LOAD',    'NO_RD',    'NO_WR',    'FETCH'],
   "AND"   : ['F_A_AND_B',  'REG', 'REG',  'REG',   'LOAD_CC',    'NO_RD',    'NO_WR',    'FETCH'],
   "NOT"   : ['F_A_NOT',    'REG', 'x',    'REG',   'LOAD_CC',    'NO_RD',    'NO_WR',    'FETCH'],
   "OR"    : ['F_A_OR_B',   'REG', 'REG',  'REG',   'LOAD_CC',    'NO_RD',    'NO_WR',    'FETCH'],
   "XOR"   : ['F_A_XOR_B',  'REG', 'REG',  'REG',   'LOAD_CC',    'NO_RD',    'NO_WR',    'FETCH'],
   "CMI"   : ['F_A',        'PC',  'x',    'MAR',   'NO_LOAD',    'NO_RD',    'NO_WR',    'CMI1'],
   "CMI1"  : ['F_A_PLUS_1', 'PC',  'x',    'PC',    'NO_LOAD',    'MEM_RD',   'NO_WR',    'CMI2'],
   "CMI2"  : ['F_A_MINUS_B','REG', 'MDR',  'NONE',  'LOAD_CC',    'NO_RD',    'NO_WR',    'FETCH'],
   "CMR"   : ['F_A_MINUS_B','REG', 'REG',  'NONE',  'LOAD_CC',    'NO_RD',    'NO_WR',    'FETCH'],
   "ASHR"  : ['F_A_ASHR',   'REG', 'x',    'REG',   'LOAD_CC',    'NO_RD',    'NO_WR',    'FETCH'],
   "LSHL"  : ['F_A_SHL',    'REG', 'x',    'REG',   'LOAD_CC',    'NO_RD',    'NO_WR',    'FETCH'],
   "LSHR"  : ['F_A_LSHR',   'REG', 'x',    'REG',   'LOAD_CC',    'NO_RD',    'NO_WR',    'FETCH'],
   "ROL"   : ['F_A_ROL',    'REG', 'x',    'REG',   'LOAD_CC',    'NO_RD',    'NO_WR',    'FETCH'],
   "MOV"   : ['F_B',        'x',   'REG',  'REG',   'NO_LOAD',    'NO_RD',    'NO_WR',    'FETCH'],
   "LDA"   : ['F_A',        'PC',  'x',    'MAR',   'NO_LOAD',    'NO_RD',    'NO_WR',    'LDA1'],
   "LDA1"  : ['F_A_PLUS_1', 'PC',  'x',    'PC',    'NO_LOAD',    'MEM_RD',   'NO_WR',    'LDA2'],
   "LDA2"  : ['F_A',        'MDR', 'x',    'MAR',   'NO_LOAD',    'NO_RD',    'NO_WR',    'LDA3'],
   "LDA3"  : ['x',          'x',   'x',    'NONE',  'NO_LOAD',    'MEM_RD',   'NO_WR',    'LDA4'],
   "LDA4"  : ['F_A',        'MDR', 'x',    'REG',   'LOAD_CC',    'NO_RD',    'NO_WR',    'FETCH'],
   "STA"   : ['F_A',        'PC',  'x',    'MAR',   'NO_LOAD',    'NO_RD',    'NO_WR',    'STA1'],
   "STA1"  : ['F_A_PLUS_1', 'PC',  'x',    'PC',    'NO_LOAD',    'MEM_RD',   'NO_WR',    'STA2'],
   "STA2"  : ['F_A',        'MDR', 'x',    'MAR',   'NO_LOAD',    'NO_RD',    'NO_WR',    'STA3'],
   "STA3"  : ['F_B',        'x',   'REG',  'MDR',   'NO_LOAD',    'NO_RD',    'NO_WR',    'STA4'],
   "STA4"  : ['x',          'x',   'x',    'NONE',  'NO_LOAD',    'NO_RD',    'MEM_WR',   'FETCH'],
   "STR"   : ['F_A',        'REG', 'x',    'MAR',   'NO_LOAD',    'NO_RD',    'NO_WR',    'STR1'],
   "STR1"  : ['F_B',        'x',   'REG',  'MDR',   'NO_LOAD',    'NO_RD',    'NO_WR',    'STR2'],
   "STR2"  : ['x',          'x',   'x',    'NONE',  'NO_LOAD',    'NO_RD',    'MEM_WR',   'FETCH'],
   "JSR"   : ['F_A_MINUS_1','SP',  'x',    'SP',    'NO_LOAD',    'NO_RD',    'NO_WR',    'JSR1'],
   "JSR1"  : ['F_A',        'SP',  'x',    'MAR',   'NO_LOAD',    'NO_RD',    'NO_WR',    'JSR2'],
   "JSR2"  : ['F_A_PLUS_1', 'PC',  'x',    'MDR',   'NO_LOAD',    'NO_RD',    'NO_WR',    'JSR3'],
   "JSR3"  : ['F_A',        'PC',  'x',    'MAR',   'NO_LOAD',    'NO_RD',    'MEM_WR',   'JSR4'],
   "JSR4"  : ['x',          'x',   'x',    'NONE',  'NO_LOAD',    'MEM_RD',   'NO_WR',    'JSR5'],
   "JSR5"  : ['F_A',        'MDR', 'x',    'PC',    'NO_LOAD',    'NO_RD',    'NO_WR',    'FETCH'],
   "LDSF"  : ['F_A',        'PC',  'x',    'MAR',   'NO_LOAD',    'NO_RD',    'NO_WR',    'LDSF1'],
   "LDSF1" : ['F_A_PLUS_1', 'PC',  'x',    'PC',    'NO_LOAD',    'MEM_RD',   'NO_WR',    'LDSF2'],
   "LDSF2" : ['F_A_PLUS_B', 'MDR', 'SP',   'MAR',   'NO_LOAD',    'NO_RD',    'NO_WR',    'LDSF3'],
   "LDSF3" : ['x',          'x',   'x',    'NONE',  'NO_LOAD',    'MEM_RD',   'NO_WR',    'LDSF4'],
   "LDSF4" : ['F_A',        'MDR', 'x',    'REG',   'NO_LOAD',    'NO_RD',    'NO_WR',    'FETCH'],
   "LDSP"  : ['F_A',        'REG', 'x',    'SP',    'NO_LOAD',    'NO_RD',    'NO_WR',    'FETCH'],
   "POP"   : ['F_A',        'SP',  'x',    'MAR',   'NO_LOAD',    'NO_RD',    'NO_WR',    'POP1'],
   "POP1"  : ['F_A_PLUS_1', 'SP',  'x',    'SP',    'NO_LOAD',    'MEM_RD',   'NO_WR',    'POP2'],
   "POP2"  : ['F_A',        'MDR', 'x',    'REG',   'NO_LOAD',    'NO_RD',    'NO_WR',    'FETCH'],
   "PUSH"  : ['F_A_MINUS_1','SP',  'x',    'MAR',   'NO_LOAD',    'NO_RD',    'NO_WR',    'PUSH1'],
   "PUSH1" : ['F_A',        'REG', 'x',    'MDR',   'NO_LOAD',    'NO_RD',    'NO_WR',    'PUSH2'],
   "PUSH2" : ['F_A_MINUS_1','SP',  'x',    'SP',    'NO_LOAD',    'NO_RD',    'MEM_WR',   'FETCH'],
   "RTN"   : ['F_A',        'SP',  'x',    'MAR',   'NO_LOAD',    'NO_RD',    'NO_WR',    'RTN1'],
   "RTN1"  : ['F_A_PLUS_1', 'SP',  'x',    'SP',    'NO_LOAD',    'MEM_RD',   'NO_WR',    'RTN2'],
   "RTN2"  : ['F_A',        'MDR', 'x',    'PC',    'NO_LOAD',    'NO_RD',    'NO_WR',    'FETCH'],
   "STSF"  : ['F_A',        'PC',  'x',    'MAR',   'NO_LOAD',    'NO_RD',    'NO_WR',    'STSF1'],
   "STSF1" : ['F_A_PLUS_1', 'PC',  'x',    'PC',    'NO_LOAD',    'MEM_RD',   'NO_WR',    'STSF2'],
   "STSF2" : ['F_A_PLUS_B', 'MDR', 'SP',   'MAR',   'NO_LOAD',    'NO_RD',    'NO_WR',    'STSF3'],
   "STSF3" : ['F_A',        'REG', 'x',    'MDR',   'NO_LOAD',    'NO_RD',    'NO_WR',    'STSF4'],
   "STSF4" : ['x',          'x',   'x',    'NONE',  'NO_LOAD',    'NO_RD',    'MEM_WR',   'FETCH'], # NOTE: bug exists is SV code. NO_LOAD exists twice.
   "ADDSP" : ['F_A',        'PC',  'x',    'MAR',   'NO_LOAD',    'NO_RD',    'NO_WR',    'ADDSP1'],
   "ADDSP1": ['F_A_PLUS_1', 'PC',  'x',    'PC',    'NO_LOAD',    'MEM_RD',   'NO_WR',    'ADDSP2'],
   "ADDSP2": ['F_A_PLUS_B', 'MDR', 'SP',   'SP',    'NO_LOAD',    'NO_RD',    'NO_WR',    'FETCH'],
   "STSP"  : ['F_A',        'SP',  'x',    'REG',   'NO_LOAD',    'NO_RD',    'NO_WR',    'FETCH'],
   "NEG"   : ['F_A_NOT',    'REG', 'x',    'REG',   'NO_LOAD',    'NO_RD',    'NO_WR',    'NEG1'],
   "NEG1"  : ['F_A_PLUS_1', 'REG', 'x',    'REG',   'NO_LOAD',    'NO_RD',    'NO_WR',    'FETCH'],
};

########################
# Main Subroutine
########################

def main():
   parser = OptionParser();
   parser.add_option("-v", "--version", action = "store_true",
                     dest = "get_version", default = False);
   parser.add_option("-r", "--run", action = "store_true",
                     dest = "run_only", default = False);
   parser.add_option("-n", "--norandom", action = "store_false",
                     dest = "randomize_memory", default = True);
   parser.add_option("-t", "--transcript", action = "store_true",
                     dest = "create_transcript", default = False);
   parser.add_option("-q", "--quiet", action = "store_true",
                     dest = "quiet_mode", default = False);
   parser.add_option("-g", "--grade", default = "", type = "str",
                     action = "store", dest = "check_file");
   parser.add_option("-p", "--pipe", default = False,
                     dest = "pipe", action = "store_true");

   (options, args) = parser.parse_args();
   if (options.get_version):
      print("version: " + str(version));
      exit();

   global run_only;
   run_only = options.run_only;

   global print_per;
   if (options.quiet_mode):
      print_per = "q";

   global check_file;
   if (options.check_file): #empty string is false
      check_file = options.check_file;
      print_per = "q";

   global randomize_memory;
   randomize_memory = options.randomize_memory;

   global create_transcript;
   create_transcript = options.create_transcript;

   date = datetime.now();

   tran("User: " + getuser() + "\n");
   tran("Date: " + date.strftime("%a %b %d %Y %I:%M:%S%p") + "\n");
   tran("Arguments: " + str(args) + "\n\n");

   global list_lines;
   if (options.pipe): # reading list file from assembler
      while(True):
         try:
            line = raw_input();
            if (len(line) > 0): #reading will grab empty lines
               list_lines.append(line);
         except EOFError:
            break;
   else:
      if (len(args) < 1): #args takes out flags and argv[0]
         usage();
      list_filename = args.pop(0);
      global list_fh;
      try:
         list_fh = open(list_filename, "r");
      except:
         print("Failed to open list_file");
         exit();
      # read all lines from list_fh, store in array,
      list_lines = list_fh.readlines();
   
   list_lines.pop(0); # remove 'addr data  label   opcode  operands'
   list_lines.pop(0); # remove '---- ----  -----   ------  --------'

   global sim_fh;
   global quit_after_sim_file;
   # sim file is optional (read input from STDIN if not specified)
   if (len(args) > 0):
      sim_filename = args.pop(0);
      if (check_file):
         quit_after_sim_file = True;
      try:
         sim_fh = open(sim_filename, "r");
      except:
         print("Failed to open sim_file\n");
         exit();
   elif (check_file): 
      run_only = True; # no simulator file and grading, just run

   init();

   interface(sim_fh); #start taking input from user
   save_tran(); #save transcript

   if (sim_fh != None): sim_fh.close();
   if (list_fh != None): list_fh.close();

# initalizes the simulator
def init():
   get_labels();

   init_p18240(); #put p18240 into a known state
   init_memory(); #initalize the memory

# prints usage for simulator
def usage():
   tran_print("./sim240 [list_file] [sim_file]");
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
      labels[label] = addr;

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
      run(0, "");
      if (check_file): # in grading mode
         check_state(check_file);
      done = True;

   while (not done):
      tran("> ");
      if (not taking_user_input):
          line = input_fh.readline();
          if (len(line) == 0):
            taking_user_input = True;
            if (quit_after_sim_file):
               check_state(check_file);
               done = True;
            continue;
          if (not check_file): #in grading mode
            tran_print(line.rstrip("\n"));
      else:
         try:
            line = raw_input("> ");
         except EOFError:
            print("\nUnexpected input, did you forget to quit?");
            exit();
         tran(line);

      # assume user input is valid until discovered not to be
      valid = True;
      #line = line.upper(); #should be independent of case
      if (match(menu["quit"], line, re.IGNORECASE)):
         done = True;
      elif (match(menu["help"], line, re.IGNORECASE)):
         print_help();
      elif (match(menu["reset"], line, re.IGNORECASE)):
         init();
      elif (match(menu["run"], line, re.IGNORECASE)):
         matchObj = match(menu["run"], line, re.IGNORECASE);
         run(matchObj.group(2), matchObj.group(3));
      elif (match(menu["step"], line, re.IGNORECASE)):
         if (print_per == "i"): tran_print(wide_header);
         step();
         if (print_per == "i"): tran_print(get_state());
      elif (match(menu["ustep"], line, re.IGNORECASE)):
         if (print_per != "q"): tran_print(wide_header);
         cycle();
         if (print_per != "q"): tran_print(get_state());
      elif (match(menu["break"], line, re.IGNORECASE)):
         matchObj = match(menu["break"], line, re.IGNORECASE);
         set_breakpoint(matchObj.group(1));
      elif (match(menu["clear"], line, re.IGNORECASE)):
         matchObj = match(menu["clear"], line, re.IGNORECASE);
         clear_breakpoint(matchObj.group(1));
      elif (match(menu["lsbrk"], line, re.IGNORECASE)):
         list_breakpoints();
      elif (match(menu["load"], line, re.IGNORECASE)):
         matchObj = match(menu["load"], line, re.IGNORECASE);
         load(matchObj.group(1));
      elif (match(menu["save"], line, re.IGNORECASE)):
         matchObj = match(menu["save"], line, re.IGNORECASE);
         save(matchObj.group(1));
      elif (match(menu["set_reg"], line, re.IGNORECASE)):
         matchObj = match(menu["set_reg"], line, re.IGNORECASE);
         set_reg(matchObj.group(1), matchObj.group(2));
      elif (match(menu["get_reg"], line, re.IGNORECASE)):
         matchObj = match(menu["get_reg"], line, re.IGNORECASE);
         get_reg(matchObj.group(1));
      elif (match(menu["set_mem"], line, re.IGNORECASE)):
         matchObj = match(menu["set_mem"], line, re.IGNORECASE);
         set_memory(matchObj.group(2), matchObj.group(3), 1);
      elif (match(menu["get_mem"], line, re.IGNORECASE)):
         matchObj = match(menu["get_mem"], line, re.IGNORECASE);
         fget_memory({"lo" : matchObj.group(2),
                      "hi" : matchObj.group(4)});
      elif (match(menu["check"], line, re.IGNORECASE)):
         matchObj = match(menu["check"], line, re.IGNORECASE);
         check_state(matchObj.group(1));
      elif (match("^$", line, re.IGNORECASE)): # user just struck enter
         pass; # something needs to be here for python
      else:
         valid = False;

      if (not valid):
         tran_print("Invalid input. Type 'help' for help.");

# prints help message
def print_help():
   help_msg = '';
   help_msg += "\n";
   help_msg += "quit,q,exit             Quit the simulator.\n";
   help_msg += "help,h,?                Print this help message.\n";
   help_msg += "step,s                  Simulate one instruction.\n";
   help_msg += "ustep,u                 Simulate one micro-instruction.\n";
   help_msg += "run,r [n]               Simulate the next n instructions.\n";
   help_msg += "run nu                  Same as above, but print ever ustep\n";
   help_msg += "break [addr/label]      Set a breakpoint at [addr] or [label].\n";
   help_msg += "lsbrk                   List all set breakpoints.\n";
   help_msg += "clear [addr/label/*]    Clear breakpoint at [addr]/[label], or clear all.\n";
   help_msg += "reset                   Reset the processor to initial state.\n";
   help_msg += "save [file]             Save the current state to a file.\n";
   help_msg += "load [file]             Load the state from a given file.\n";
   help_msg += "check [file]            Checks state against state described in file.\n"''
   help_msg += "\n";
   help_msg += "You may set registers like so:          PC=100\n";
   help_msg += "You may view register contents like so: PC?\n";
   help_msg += "You may view the register file like so: R*?\n";
   help_msg += "You may view all registers like so:     *?\n";
   help_msg += "\n";
   help_msg += "You may set memory like so:  m[00A0]=100\n";
   help_msg += "You may view memory like so: m[00A0]? or with a range: m[0:A]?\n";
   help_msg += "\n";
   help_msg += "Note: All constants are interpreted as hexadecimal.";
   tran_print(help_msg);

# initalizes the processor (registers zeroed, state = FETCH)
def init_p18240():
   global cycle_num;
   cycle_num = 0;

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

# initalizes the memory, sets memory locations in list file
def init_memory():
   global memory;
   memory = {};
   int_max = (1 << 16) - 1; # 16-bit ints
   global randomize_memory;
   if (randomize_memory):
      for addr in xrange(1 << 16):
         data = to_4_digit_uc_hex(randint(0, int_max));
         addr = to_4_digit_uc_hex(addr);
         set_memory(addr, data, 0);

   global list_lines;
   for line in list_lines:
      arr = line.split(" ");
      addr = arr[0];
      data = arr[1];
      memory[addr] = [data.lower(),1];

# Run simulator for n instructions
# If n is undefined, run indefinitely
# In either case, the exception is to stop
# at breakpoints or the STOP microinstruction
# print_per_requested is how often state is printer (per U-instruction,
# per Instruction, Quiet)
def run(num, print_per_requested):
   if (not num): 
      num = (1<<32);
   else:
      num = int(num);
   global print_per;
   print_per_tmp = print_per;
   if (print_per_requested): print_per = print_per_requested;
   if (print_per != "q"): tran_print(wide_header);

   for i in xrange(num):
      step();
      if (print_per == "i"): tran_print(get_state());
      if (state["PC"] in breakpoints):
         tran_print("Hit breakpoint at " + state["PC"] + ".\n");
         break;

      if (state["STATE"] == "STOP1"):
         break;

   print_per = print_per_tmp;

# Simulate one instruction
def step():
   cycle(); # do-while in python
   if (print_per == "u"): tran_print(get_state());
   while (state["STATE"] != "FETCH" and state["STATE"] != "STOP1"):
      cycle();
      if (print_per == "u"): tran_print(get_state());

# Set a break point at a given address or label.
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
   elif (match("^[0-9a-f]{1,4}$", arg, re.IGNORECASE)):
      addr = to_4_digit_uc_hex(int(arg,16));
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

# Clears a breakpoint at a given address or label
def clear_breakpoint(arg):
   clear_all = False;
   is_label = False;

   if (match("^'(\w+)'$", arg)):
      label = match("^'(\w+)'$", arg).group(1);
      is_label = True;
   elif (match("^[0-9a-f]{1,4}$", arg, re.IGNORECASE)):
      addr = to_4_digit_uc_hex(int(arg,16));
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

# Loads state from a given state file (usually made by save). 
def load(filename):
   tran_print("Loading from " + filename + "...");
   try:
      fh = open(filename, "r");
   except:
      tran_print("Unable to read from " + filename);
      return;
   lines = fh.readlines();
   lines.pop(0); #removes "Breakpoints"
   line = lines.pop(0);
   while (len(line) > 1): # breakpoints to add still
      set_breakpoint(line);
      line = lines.pop(0); 
   lines.pop(0); # State:
   values = lines.pop(0).split();
   labels = wide_header.split();
   global state;
   for i in xrange(len(labels)): # load register values
      label = labels[i];
      if (label in state):
         state[label] = values[i];
      elif (match("^\s*R?\s*(\d*)?\s*$", label)):
         matchObj = match("^\s*R?\s*(\d*)?\s*$", label);
         reg_num = int(matchObj.group(1));
         state["regFile"][reg_num] = values[i];
      elif (label == "Cycle"):
         global cycle_num;
         cycle_num = int(values[i]);
      else: # ZNCV register
         flag_num = 0;
         for flag in ["Z", "N", "C", "V"]:
            state[flag] = values[i][flag_num];
            flag_num += 1;
   lines.pop(0); # newline
   lines.pop(0); # Memory:
   while (len(lines) > 0): # load memory values
      line = lines.pop(0);
      addr = line[4:8];
      value = line[11:15];
      set_memory(addr, value, 1);
   return;

# Save state of processor, memory, and breakpoints to a file. State
# file can be used to check against the current processor state, or can
# be loaded into simulation
def save(filename):
   tran_print("Saving to " + filename + "...");
   try:
      fh = open(filename, "w");
   except:
      tran_print("Unable to write to " + filename);
      return;
   fh.write("Breakpoints:\n");
   for key in breakpoints:
      fh.write(key + "\n");
   fh.write("\nState:\n");
   fh.write(get_state() + "\n\n");
   fh.write("Memory:\n");
   fget_memory({"fh" : fh,
                "lo" : '0',
                "hi" : "ffff",
                "zeros" : 0});
   fh.close();

# Sets the value of a register
def set_reg(reg_name, value):
   global state;
   reg_name = reg_name.upper(); #keys stored as uppercase
   value = to_4_digit_uc_hex(int(value,16));
   if (match('^R([0-7])$', reg_name, re.IGNORECASE)):
      matchObj = match('^R([0-7])$', reg_name, re.IGNORECASE);
      state["regFile"][int(matchObj.group(1))] = value;
   elif (match("^[ZNCV]$", reg_name)):
      if (match("^[01]$", reg_name)):
         state[reg_name] = value;
      else:
         tran_print("Value must be 0 or 1 for this register.");
   else:
      state[reg_name] = to_4_digit_uc_hex(int(value,16));

# Gets the value of a register
def get_reg(reg_name):
   reg_name = reg_name.upper();
   if (reg_name == "*"):
      tran_print(get_state());
   elif (reg_name == "R*"):
      print_regfile();
   elif (match("R([0-7])", reg_name, re.IGNORECASE)):
      reg_num = int(match("R([0-7])", reg_name, re.IGNORECASE).group(1));
      tran_print("R%d: %s" % (reg_num, state["regFile"][reg_num]));
   else:
      value = state[reg_name];
      tran_print("%s: %s" % (reg_name, value));

# Gets a string containing all the state information
def get_state():
   (Z,N,C,V) = (state["Z"], state["N"], state["C"], state["V"]);
   state_info = "%0.4d" % cycle_num;
   state_info += " " * (7 - len(state["STATE"]));
   state_info += "%s %s %s %s %s%s%s%s %s %s" % (state["STATE"], state["PC"],
                                            state["IR"], state["SP"],
                                            Z, N, C, V,
                                            state["MAR"], state["MDR"]);
   for reg in state["regFile"]:
      state_info += " " + reg;
   return state_info;

# prints the state of R0-R7
def print_regfile():
   even = False;
   for index in xrange(0,8,2):
      value = state["regFile"][index];
      reg_str = "R%d: %s \t" % (index, value);
      value = state["regFile"][index+1];
      reg_str += "R%d: %s" %(index+1, value);
      tran_print(reg_str);

# Sets a memory value. The valid bit specifies if it will be store in 
# a save state file. By heuristic, memory is invalid until changed.
def set_memory(addr, value, valid):
   addr_hex = to_4_digit_uc_hex(int(addr,16));
   value_hex = to_4_digit_uc_hex(int(value,16));
   memory[addr_hex] = [value, valid];


# Gets the state of a selection of memory, arguments are passed in a dict
# get_zeros specifies if zeros will be printed when they are reached
# lo - the inclusive lower bound of memory
# hi - the inclusive upper bound
# fh - file handle to write memory state to, default to STDOUT
def fget_memory(args):
   if ("zeros" in args):
      print_zeros = args["zeros"];
   else:
      print_zeros = True;
   lo = int(args["lo"], 16);
   if ("hi" in args and args["hi"] != None):
      hi = int(args["hi"],16);
   else:
      hi = lo;

   if (lo > hi):
      tran_print("Did you mean mem[%x:%x]?" % (hi,lo));
      return;

   for index in xrange(lo, hi+1):
      addr = ("%.4x" % (index)).upper();
      if (addr in memory):
         value = memory[addr][0];
      else:
         value = "0000";
      if (not (value == "0000" and not print_zeros)):
         value_no_regs = "%.4x" % (int(value,16) & 0xffc0);
         state_str = hex_to_state(value_no_regs);
         rd = bs(int(value,16), "5:3");
         rs = bs(int(value,16), "2:0");
         mem_val = "mem[%s]: %s %s %d %d" % (addr, value,
                                         state_str, rd, rs);
         if ("fh" in args and memory[addr][1]): #only save used memory
            args["fh"].write(mem_val + "\n");
         elif ("fh" not in args):
            tran_print(mem_val);

# Checks the state of the processor and memory against a given state file
# Prints out differences. Registers set to XXXX/xxxx in state file are
# ignored for comparison. Memory not specified in state file is also ignored
# Breakpoints are always ignored.
# TODO - make regex to match to any x/xx/xxx/xxxx.
def check_state(state_file):
   try:
      fh = open(state_file, "r");
   except:
      tran_print("Failed to open state file");
      return;
   lines = fh.readlines();
   while (not lines[0].startswith("State")):
      lines.pop(0);
   lines.pop(0); # removes "State: line
   file_state = lines.pop(0).split();
   sim_state = get_state().split();
   labels = wide_header.split();
   for i in xrange(len(file_state)):
      if (file_state[i].upper() != "XXXX" and file_state[i] != sim_state[i]):
         tran_print(labels[i] + " differs: sim = " + sim_state[i]
                         + ", file = " + file_state[i]);
   lines.pop(0); # removes newline
   lines.pop(0); # removes "Memory:"
   for line in lines:
      addr = line[4:8].upper();
      file_val = line[11:15].upper();
      sim_val = memory[addr][0].upper();
      if (file_val != sim_val):
         tran_print("Mem[" + addr + "] differs: sim = " + sim_val +
                            ", file = " + file_val);



########################
# Simulator Code
########################

# Simulate one cycle in the processor
def cycle():
   # Control Path ###
   cp_out = control();

   ### Start of ALU ###
   rf_selA = bs(int(state["IR"],16), "5:3");
   rf_selB = bs(int(state["IR"],16), "2:0");

   regA = state["regFile"][rf_selA]; #strings, since mux could select this
   regB = state["regFile"][rf_selB];

   inA = int(mux({"PC" : state["PC"], "MDR" : state["MDR"], "SP" : state["SP"],
              "REG" : regA}, cp_out["srcA"]), 16);
   inB = int(mux({"PC" : state["PC"], "MDR" : state["MDR"], "SP" : state["SP"],
              "REG" : regB}, cp_out["srcB"]), 16);

   alu_in = {"alu_op" : cp_out["alu_op"], "inA" : inA, "inB" : inB};
   alu_out = alu(alu_in);
   ### End of ALU ##

   ### Memory ###
   mem_data = memory_sim({"re" : cp_out["re"], "we" : cp_out["we"],
                      "data" : state["MDR"], "addr" : state["MAR"]});

   ### Sequential Logic ###
   dest = cp_out["dest"];

   if (dest != "NONE"):
      if (dest == "REG"):
         state["regFile"][rf_selA] = alu_out["alu_result"];
      else:
         state[dest] = alu_out["alu_result"];

   # store memory output to MDR
   if (cp_out["re"] == "MEM_RD"):
      state["MDR"] = mem_data;

   # load condition codes
   if (cp_out["load_CC"] == "LOAD_CC"):
      for flag in ["Z", "N", "C", "V"]:
         state[flag] = alu_out[flag];

   
   state["STATE"] = cp_out["next_control_state"];

   global cycle_num;
   cycle_num += 1;

##################################################
############# CONTROL PATH CODE ##################
##################################################

# gets the micro instruction assocated with a given state,
# sets next state values that are dependent on flags
def control():

   # python is bad with globals
   nextState_logic["DECODE"][7] = hex_to_state(state["IR"]);
   nextState_logic["BRN"][7] = "BRN2" if int(state["N"]) else "BRN1";
   nextState_logic["BRZ"][7] = "BRZ2" if int(state["Z"]) else "BRZ1";
   nextState_logic["BRV"][7] = "BRV2" if int(state["V"]) else "BRV1";
   nextState_logic["BRC"][7] = "BRC2" if int(state["C"]) else "BRC1";
   curr_state = state["STATE"];

   output = nextState_logic[curr_state];

   uinstr = {
      "alu_op" : output[0],
      "srcA" : output[1],
      "srcB" : output[2],
      "dest" : output[3],
      "load_CC" : output[4],
      "re" : output[5],
      "we" : output[6],
      "next_control_state" : output[7],
   };

   return uinstr;

# Simulates the P18240's ALU. Args values are ints, values are returned
# as strings.
def alu(args):
   opcode = args["alu_op"];
   inA = args["inA"];
   inB = args["inB"];

   Z = 0;
   C = 0;
   N = 0;
   V = 0;

   if (opcode == "F_A"):
      out = inA;
   elif (opcode == "F_A_PLUS_1"):
      out = bs(inA+1, '15:0');
      C = bs(inA+1, "16");
      V = ~bs(inA, "15") & bs(out, "15");
   elif (opcode == "F_A_PLUS_B"):
      out = bs(inA+inB, '15:0');
      C = bs(inA+inB, "16");
      V = (bs(inA,"15") & bs(inB,"15") & ~bs(out,"15")) | (~bs(inA,"15") & ~bs(inB,"15") & bs(out,"15"));
   elif (opcode == "F_A_PLUS_B_1"):
      out = bs(inA + inB + 1,'15:0');
      C = bs(inA + inB + 1,"16");
      V = (bs(inA,"15") & bs(inB,"15") & ~bs(out,"15")) | (~bs(inA,"15") & ~bs(inB,"15") & bs(out,"15"));
   elif (opcode == "F_A_MINUS_B_1"):
      out = bs(inA - inB - 1,'15:0'); # A-B-1 (set carry below)
      C = ((inB + 1) >= inA);
      V = (bs(inA,"15") & ~bs(inB,"15") & ~bs(out,"15")) | (~bs(inA,"15") & bs(inB,"15") & bs(out,"15"));
   elif (opcode == "F_A_MINUS_B"):
      out = bs(inA - inB,'15:0'); # A-B (set carry below)
      C = 1 if (inB >= inA) else 0;
      V = (bs(inA,"15") & ~bs(inB,"15") & ~bs(out,"15")) | (~bs(inA,"15") & bs(inB,"15") & bs(out,"15"));
   elif (opcode == "F_A_MINUS_1"):
      out = bs(inA - 1, "15:0");
      C = bs(inA - 1, "16");
      V = ~bs(inA,"15") & bs(out,"15");
   elif (opcode == "F_B"):
      out = inB;
   elif (opcode == "F_A_NOT"):
      out = bs(~inA, "15:0");
   elif (opcode == "F_A_AND_B"):
      out = inA & inB;
   elif (opcode == "F_A_OR_B"):
      out = inA | inB;
   elif (opcode == "F_A_XOR_B"):
      out = inA ^ inB;
   elif (opcode == "F_A_SHL"):
      C = bs(inA << 1, "15");
      out = bs(inA << 1, "15:0");
   elif (opcode == "F_A_ROL"):
      out = (bs(inA, "14:0") << 1) + int(state["C"]);
      C = bs(inA, "15");
   elif (opcode == "F_A_LSHR"):
      C = bs(inA, "0");
      out = bs(inA, "15:1"); #CHANGED FROM SIM240!!!!
   elif (opcode == "F_A_ASHR"):
      C = bs(inA, "0");
      out = (bs(inA,"15") << 15) + bs(inA, "15:1");
   elif (opcode == "x"):
      out = 0;
   else:
      print("Error: invalid alu opcode $opcode");

   N = bs(out, "15");
   Z = 1 if (out == 0) else 0;

   rv = {
      "alu_result" : ("%.4x" % out).upper(),
      "Z" : str(Z),
      "N" : str(N),
      "C" : str(C),
      "V" : str(V),
   };

   return rv;

# Simulates a memory.
# Arguments are specified in a hash:
# If value for 're' key is 'MEM_RD', read from memory.
# If value for 'we' key is 'MEM_WR', write to memory.
# Reading and writing both use the value of the 'addr' key.
# Writing writes the value of the 'data_in' key.
# Return value:
# Returns the data stored at 'addr' when reading; 0000 otherwise.
def memory_sim(args):
   re = args["re"];
   we = args["we"];
   data_in = args["data"];
   addr = args["addr"];

   data_out = "0000"; # data_in would mimic bus more accurately...
   if (re == "MEM_RD") and (addr in memory):
      data_out = memory[addr][0];
   if (we == "MEM_WR"):
      memory[addr][0] = data_in;
      memory[addr][1] = 1;

   return data_out;

# Simulates a multiplexor. The inputs to be selected must be in a dict
def mux(inputs, sel):
   if (sel == "x"):
      return '0';

   return inputs[sel];


########################
# Supporting Subroutines
########################

# adds a new line to the transcript - line doesn't include \n
def tran(line):
   global transcript;
   if (create_transcript):
      transcript += (line);

# add the string to the transcript and print to file
def tran_print(line):
   tran(line + "\n"); 
   print(line);

# Bitslice subroutine.
# First argument is a number, second argument is a string which indicates
# which bits you want to extract. This follows verilog format
# That is, '5' will extract bit 5, '5:2' will extract bits 5 to 2.
# The return value is shifted down so that the least significant selected
# bit moves down to the least significant position.
def bs(bits, indices):
   matchObj = match("(\d+):(\d+)", indices);
   if (matchObj != None):
      hi = int(matchObj.group(1));
      lo = int(matchObj.group(2));
      return (bits >> lo) & ((2 << (hi - lo)) - 1);
   else:
      index = int(match("(\d+)", indices).group(1));
      return (bits >> index) & 1;

# Takes a hexadecimal number in canonical form and outputs the
# string corresponding to that opcode.
def hex_to_state(hex_value):
   bin_val = bin(int(hex_value, 16));
   bin_val = bin_val[2:]; #removes starting '0b'
   while (len(bin_val) < 16): #adds starting zeros
      bin_val = "0" + bin_val;

   key = bin_val[0:2] + "_" + bin_val[2:6] + "_" + bin_val[6:10];

   if (key in uinst_bin_keys):
      state = uinst_bin_keys[key];
   else:
      state = 'UNDEF';
   return state;

# Saves the transcript to transcript.txt
def save_tran():
   if (create_transcript):
      try:
         tran_fh = open("transcript.txt", "w");
      except:
         exit();
      tran_fh.write(transcript);
      tran_fh.close();

# Takes a hexadecimal number as input and outputs a canonical form
# The cacnonical form is a 4 digit uppercase hexadecimal number
# Input can be 1 to 4 digits with any case.
def to_4_digit_uc_hex(num):
   return ("%.4x" % num).upper();

# Signal handler for SIGINTs
def sigint_handler(signal, frame):
   print("\nUnexpected input, did you forget to quit?");
   exit();

signal.signal(signal.SIGINT, sigint_handler);
main();
