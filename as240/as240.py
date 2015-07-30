#!/usr/bin/python

from __future__ import print_function
from optparse import OptionParser
import sys
import re
import random

class ParseError(Exception):

    def __init__(self, line_number, reason_text):
        self.line_number = line_number
        self.reason_text = reason_text

    def __str__(self):
        return ("Parse Error on line " + str(self.line_number) + ":  " + str(self.reason_text))

class SyntaxError(Exception):

    def __init__(self, line_number, reason_text):
        self.line_number = line_number
        self.reason_text = reason_text

    def __str__(self):
        return ("Syntax Error on line " + str(self.line_number) + ":  " + str(self.reason_text))

class OpcodeInfo:

    opcode_info = {'ADD' : { 'format' : 'short',
                             'field1' : 'op1',
                             'field2' : 'op2',
                             'num_operands' : 2,
                             'op1_type' : 'register',  # register, number
                             'op2_type' : 'register',
                             'encoding' : '0000111000' },
                   'ADDSP' : { 'format' : 'long',
                               'field1' : 'zero',
                               'field2' : 'zero',
                               'field3' : 'op1',  # Long format, 2nd word
                               'num_operands' : 1,
                               'op1_type' : 'number',
                               'encoding' : '0000111100' },
                   'AND' : { 'format' : 'short',
                             'field1' : 'op1',
                             'field2' : 'op2',
                             'num_operands' : 2,
                             'op1_type' : 'register',
                             'op2_type' : 'register',
                             'encoding' : '0001101000' },
                   'ASHR' : { 'format' : 'short',
                              'field1' : 'op1',
                              'field2' : 'op1',
                              'num_operands' : 1,
                              'op1_type' : 'register',
                              'encoding' : '0010011000' },
                   'BRA' : { 'format' : 'long',
                             'field1' : 'zero',
                             'field2' : 'zero',
                             'field3' : 'op1',
                             'num_operands' : 1,
                             'op1_type' : 'number',
                             'encoding' : '0010100000' },
                   'BRC' : { 'format' : 'long',
                             'field1' : 'zero',
                             'field2' : 'zero',
                             'field3' : 'op1',
                             'num_operands' : 1,
                             'op1_type' : 'number',
                             'encoding' : '0100100000' },
                   'BRN' : { 'format' : 'long',
                             'field1' : 'zero',
                             'field2' : 'zero',
                             'field3' : 'op1',
                             'num_operands' : 1,
                             'op1_type' : 'number',
                             'encoding' : '0010110000' },
                   'BRV' : { 'format' : 'long',
                             'field1' : 'zero',
                             'field2' : 'zero',
                             'field3' : 'op1',
                             'num_operands' : 1,
                             'op1_type' : 'number',
                             'encoding' : '0010111000' },
                   'BRZ' : { 'format' : 'long',
                             'field1' : 'zero',
                             'field2' : 'zero',
                             'field3' : 'op1',
                             'num_operands' : 1,
                             'op1_type' : 'number',
                             'encoding' : '0010101000' },
                   'CMI' : { 'format' : 'long',
                             'field1' : 'zero',
                             'field2' : 'zero',
                             'field3' : 'op2',
                             'num_operands' : 2,
                             'op1_type' : 'register',
                             'op2_type' : 'number',
                             'encoding' : '0100010000' },
                   'CMR' : { 'format' : 'short',
                             'field1' : 'op1',
                             'field2' : 'op2',
                             'num_operands' : 2,
                             'op1_type' : 'register',
                             'op2_type' : 'register',
                             'encoding' : '0100011000' },
                   'DECR' : { 'format' : 'short',
                              'field1' : 'op1',
                              'field2' : 'op1',
                              'num_operands' : 1,
                              'op1_type' : 'register',
                              'encoding' : '0001011000' },
                   'INCR' : { 'format' : 'short',
                              'field1' : 'op1',
                              'field2' : 'op1',
                              'num_operands' : 1,
                              'op1_type' : 'register',
                              'encoding' : '0001010000' },
                   'JSR' : { 'format' : 'long',
                             'field1' : 'zero',
                             'field2' : 'zero',
                             'field3' : 'op1',
                             'num_operands' : 1,
                             'op1_type' : 'number',
                             'encoding' : '0011011000' },
                   'LDA' : { 'format' : 'long',
                             'field1' : 'op1',
                             'field2' : 'op1',
                             'field3' : 'op2',
                             'num_operands' : 2,
                             'op1_type' : 'register',
                             'op2_type' : 'number',
                             'encoding' : '0000010000' },
                   'LDI' : { 'format' : 'long',
                             'field1' : 'op1',
                             'field2' : 'op1',
                             'field3' : 'op2',
                             'num_operands' : 2,
                             'op1_type' : 'register',
                             'op2_type' : 'number',
                             'encoding' : '0000110000' },
                   'LDR' : { 'format' : 'short',
                             'field1' : 'op1',
                             'field2' : 'op2',
                             'num_operands' : 2,
                             'op1_type' : 'register',
                             'op2_type' : 'register',
                             'encoding' : '0000100000' },
                   'LDSF' : { 'format' : 'long',
                              'field1' : 'op1',
                              'field2' : 'op1',
                              'field3' : 'op2',
                              'num_operands' : 2,
                              'op1_type' : 'register',
                              'op2_type' : 'number',
                              'encoding' : '0100000000' },
                   'LDSP' : { 'format' : 'short',
                              'field1' : 'op1',
                              'field2' : 'op1',
                              'num_operands' : 1,
                              'op1_type' : 'register',
                              'encoding' : '0011110000' },
                   'LSHL' : { 'format' : 'short',
                              'field1' : 'op1',
                              'field2' : 'op1',
                              'num_operands' : 1,
                              'op1_type' : 'register',
                              'encoding' : '0010000000' },
                   'LSHR' : { 'format' : 'short',
                              'field1' : 'op1',
                              'field2' : 'op1',
                              'num_operands' : 1,
                              'op1_type' : 'register',
                              'encoding' : '0010010000' },
                   'MOV' : { 'format' : 'short',
                             'field1' : 'op1',
                             'field2' : 'op2',
                             'num_operands' : 2,
                             'op1_type' : 'register',
                             'op2_type' : 'register',
                             'encoding' : '0011101000' },
                   'NEG' : { 'format' : 'short',
                             'field1' : 'op1',
                             'field2' : 'op1',
                             'num_operands' : 1,
                             'op1_type' : 'register',
                             'encoding' : '0001001000' },
                   'NOT' : { 'format' : 'short',
                             'field1' : 'op1',
                             'field2' : 'op1',
                             'num_operands' : 1,
                             'op1_type' : 'register',
                             'encoding' : '0001100000' },
                   'OR' : { 'format' : 'short',
                            'field1' : 'op1',
                            'field2' : 'op2',
                            'num_operands' : 2,
                            'op1_type' : 'register',
                            'op2_type' : 'register',
                            'encoding' : '0001110000' },
                   'POP' : { 'format' : 'short',
                             'field1' : 'op1',
                             'field2' : 'op1',
                             'num_operands' : 1,
                             'op1_type' : 'register',
                             'encoding' : '0011010000' },
                   'PUSH' : { 'format' : 'short',
                              'field1' : 'op1',
                              'field2' : 'op1',
                              'num_operands' : 1,
                              'op1_type' : 'register',
                              'encoding' : '0011001000' },
                   'ROL' : { 'format' : 'short',
                             'field1' : 'op1',
                             'field2' : 'op1',
                             'num_operands' : 1,
                             'op1_type' : 'register',
                             'encoding' : '0010001000' },
                   'RTN' : { 'format' : 'short',
                             'field1' : 'zero',
                             'field2' : 'zero',
                             'num_operands' : 0,
                             'encoding' : '0011100000' },
                   'STA' : { 'format' : 'long',
                             'field1' : 'op2',
                             'field2' : 'op2',
                             'field3' : 'op1',
                             'num_operands' : 2,
                             'op1_type' : 'number',
                             'op2_type' : 'register',
                             'encoding' : '0000011000' },
                   'STOP' : { 'format' : 'short',
                              'field1' : 'zero',
                              'field2' : 'zero',
                              'num_operands' : 0,
                              'encoding' : '0011000000' },
                   'STR' : { 'format' : 'short',
                             'field1' : 'op1',
                             'field2' : 'op2',
                             'num_operands' : 2,
                             'op1_type' : 'register',
                             'op2_type' : 'register',
                             'encoding' : '0000101000' },
                   'STSF' : { 'format' : 'long',
                              'field1' : 'op1',
                              'field2' : 'op1',
                              'field3' : 'op2',
                              'num_operands' : 2,
                              'op1_type' : 'register',
                              'op2_type' : 'number',
                              'encoding' : '0100001000' },
                   'STSP' : { 'format' : 'short',
                              'field1' : 'op1',
                              'field2' : 'op1',
                              'num_operands' : 1,
                              'op1_type' : 'register',
                              'encoding' : '0011111000' },
                   'SUB' : { 'format' : 'short',
                             'field1' : 'op1',
                             'field2' : 'op2',
                             'num_operands' : 2,
                             'op1_type' : 'register',
                             'op2_type' : 'register',
                             'encoding' : '0001000000' },
                   'XOR' : { 'format' : 'short',
                             'field1' : 'op1',
                             'field2' : 'op2',
                             'num_operands' : 2,
                             'op1_type' : 'register',
                             'op2_type' : 'register',
                             'encoding' : '0001111000' },
                   }

    @classmethod
    def valid_opcode(cls, opcode):
        return opcode in cls.opcode_info

    @classmethod
    def invalid_opcode(cls, opcode):
        return not opcode in cls.opcode_info

    @classmethod
    def num_operands(cls, opcode):
        return cls.opcode_info[opcode]['num_operands']

    @classmethod
    def operand1_type(cls, opcode):
        return cls.opcode_info[opcode]['op1_type']

    @classmethod
    def operand2_type(cls, opcode):
        return cls.opcode_info[opcode]['op2_type']

    @classmethod
    def operation_size(cls, opcode):
        if cls.opcode_info[opcode]['format'] == 'short':
            return 1
        else:
            return 2

    @classmethod
    def field1_is(cls, opcode):
        return cls.opcode_info[opcode]['field1']

    @classmethod
    def field2_is(cls, opcode):
        return cls.opcode_info[opcode]['field2']

    @classmethod
    def field3_is(cls, opcode):
        return cls.opcode_info[opcode]['field3']

    @classmethod
    def encoding_is(cls, opcode):
        return cls.opcode_info[opcode]['encoding']

    @classmethod
    def format_is_long(cls, opcode):
        return cls.opcode_info[opcode]['format'] == 'long'

class AsmLine:
    """Class to represent a single line in the assembly file"""

    # Any valid ASM line matches one of the following regular expressions
    # A line without any fields
    re_blank  = re.compile("""
                           ^    # Start of line
                           \s*  # zero or more whitespace characters
                           $    # end of line
                           """, re.VERBOSE)

    # A line with only the label field
    re_label =  re.compile("""
                           ^      # Start of line
                           (\S+)  # One or more non-whitespace characters (save as group[0])
                           \s*    # Zero or more whitespace characters
                           $      # end of line
                           """, re.VERBOSE)

    # A line with a label and an opcode
    re_labop  = re.compile("""
                           ^      # Start of line
                           (\S+)  # One or more non-whitespace characters (save as group[0])
                           \s+    # One or more whitespace characters
                           (\S+)  # One or more non-whitespace characters (save as group[1])
                           \s*    # Zero or more whitespace characters
                           $      # end of line
                           """, re.VERBOSE)

    # A line with a label, opcode and one operand
    re_labop1 = re.compile("""
                           ^      # Start of line
                           (\S+)  # One or more non-whitespace characters (save as group[0])
                           \s+    # One or more whitespace characters
                           (\S+)  # One or more non-whitespace characters (save as group[1])
                           \s+    # One or more whitespace characters
                           (\S+)  # One or more non-whitespace characters (save as group[2])
                           \s*    # Zero or more whitespace characters
                           $      # end of line
                           """, re.VERBOSE)

    # A line with a label, opcode and two operands
    re_labop2 = re.compile("""
                           ^      # Start of line
                           (\S+)  # One or more non-whitespace characters (save as group[0]:label)
                           \s+    # One or more whitespace characters
                           (\S+)  # One or more non-whitespace characters (save as group[1]:opcode)
                           \s+    # One or more whitespace characters
                           (\S+)  # One or more non-whitespace characters (save as group[2]:operand1)
                           \s*    # Zero or more whitespace characters
                           ,      # A comma
                           \s*    # Zero or more whitespace characters
                           (\S+)  # One or more non-whitespace characters (save as group[3]:operand2)
                           \s*    # Zero or more whitespace characters
                           $      # end of line
                           """, re.VERBOSE)

    # A line with just an opcode (no label)
    re_opcode = re.compile("""
                           ^      # Start of line
                           \s+    # One or more whitespace characters (no label)
                           (\S+)  # One or more non-whitespace characters (save as group[0]:opcode)
                           \s*    # Zero or more whitespace characters
                           $      # end of line
                           """, re.VERBOSE)

    # A line with an opcode and a single operand (no label)
    re_op1    = re.compile("""
                           ^      # Start of line
                           \s+    # One or more whitespace characters (no label)
                           (\S+)  # One or more non-whitespace characters (save as group[0]:opcode)
                           \s+    # One or more whitespace characters
                           (\S+)  # One or more non-whitespace characters (save as group[1]:operand1)
                           \s*    # Zero or more whitespace characters
                           $      # end of line
                           """, re.VERBOSE)

    # A line with an opcode and two operands (no label)
    re_op2    = re.compile("""
                           ^      # Start of line
                           \s+    # One or more whitespace characters (no label)
                           (\S+)  # One or more non-whitespace characters (save as group[0]:opcode)
                           \s+    # One or more whitespace characters
                           (\S+)  # One or more non-whitespace characters (save as group[1]:operand1)
                           \s*    # Zero or more whitespace characters
                           ,      # A comma
                           \s*    # Zero or more whitespace characters
                           (\S+)  # One or more non-whitespace characters (save as group[2]:operand2)
                           \s*    # Zero or more whitespace characters
                           $      # end of line
                           """, re.VERBOSE)

    # Validation regular expression: matches a label
    re_vallabel  = re.compile("""
                              ^      # Start of label (string)
                              \w+    # One or more alphanumeric or underbar characters
                              $      # end of label (string)
                              """, re.VERBOSE)

    # Validation RE: checks an operand is a number (hex or label)
    re_valop_num = re.compile("""
                              ^                 # Start of operand (string)
                              (                 # either
                              \$                # the dollar sign (backspace escaped so not to be the RE end-of-line marker)
                              [0-9A-F]{1,4}     # one to four hex digits (number or letters A-F)
                              |                 # OR
                              \w+               # one or more alphanumeric or underbar characters (this is a label)
                              )                 # end of either-or
                              $                 # end of operand (string
                              """, re.VERBOSE)

    # Validation RE: checks an operand is a register specifier
    re_valop_reg = re.compile("""
                              ^      # Start of line
                              R      # The letter R
                              [0-7]  # a number between 0 and 7
                              $      # end of line
                              """, re.VERBOSE)

    # Validation RE: checks an operand is a hex number
    re_valop_hex = re.compile("""
                              ^                 # Start of operand (string)
                              \$                # the dollar sign (backspace escaped so not to be the RE end-of-line marker)
                              [0-9A-F]{1,4}     # one to four hex digits (number or letters A-F)
                              $                 # end of operand (string
                              """, re.VERBOSE)

    # Validation RE: checks an opcode is a pseudo-operation
    re_pseudo    = re.compile("""
                              ^                 # Start of operand (string)
                              \.                # A period (backspace escaped, as a period is a RE any-character marker)
                              (ORG|DW|EQU)      # Either ORG or DW or EQU
                              $                 # end of operand (string
                              """, re.VERBOSE)

    def __init__(self, line, line_number, mem_address):
        self.text = line
        self.opcode = None
        self.label  = None
        self.operand1 = None
        self.operand2 = None
        self.is_valid = False
        self.is_blank = False
        self.word1 = None        # Memory contents (i.e. assembled machine code)
        self.word2 = None
        self.line_number = line_number
        self.mem_address = mem_address
        self.is_pseudo_operation = False
        self.__parseInitial()
        self.__validate()


    def __str__(self):
        """ The List file format for the instruction.
        Will return a blank string, one or two lines.
        """
        ret_val = ""
        FORMAT_STRING = "%04X %04X  %-5s   %-6s %-8s"
        if not self.is_valid:
            return "Invalid ASM Line"
        if self.word1:
            if self.label:
                label_or_space = self.label
            else:
                label_or_space = " "

            formatted_operands = ""
            if (self.is_pseudo_operation
                or not OpcodeInfo.format_is_long(self.opcode)):
                if self.operand2:
                    formatted_operands = "%s %s" % (self.operand1,
                                                    self.operand2)
                elif self.operand1:
                    formatted_operands = self.operand1
            else:
                formatted_operands = self.operand1

            ret_val = FORMAT_STRING % (self.mem_address,
                                       self.word1,
                                       label_or_space,
                                       self.opcode,
                                       formatted_operands)
        if self.word2:
            ret_val += "\n"
            ret_val += FORMAT_STRING % (self.mem_address+1,
                                        self.word2,
                                        " ",
                                        " ",
                                        self.operand2)
        return ret_val

    def mem_str(self):
        """ Return a printable string for the memory file.
        This file just has address and data values
        """
        ret_val = ""
        FORMAT_STRING = "%04X %04X"
        if not self.is_valid:
            return "Invalid ASM Line"
        if self.word1:
            ret_val = FORMAT_STRING % (self.mem_address, self.word1)
        if self.word2:
            ret_val += "\n"
            ret_val += FORMAT_STRING % (self.mem_address+1, self.word2)
        return ret_val

    def __parseInitial(self):
        """ Break the line into fields (label, opcode, operand1, operand2).
        Remove any comments.
        """
        # remove comments
        c_index = self.text.find(';')
        if c_index > 0 :
            p_line  = self.text[:c_index]  # Parse Line.  This is my scratchpad
        else :
            p_line = self.text

        # is the line blank?
        match = self.re_blank.search(p_line)
        if match:
            self.is_valid = True
            return

        # is the line a label-only line?
        match = self.re_label.search(p_line)
        if match:
            self.is_valid = True
            self.label = match.groups()[0].upper()
            return

        # Does the line only have a label and operand?
        match = self.re_labop.search(p_line)
        if match:
            self.is_valid = True
            g = match.groups()
            self.label  = g[0].upper()
            self.opcode = g[1].upper()
            return

        # must check the two-operand versions before the one-operand, else
        # a comma without whitespace separating the operands will get viewed as
        # a single operand
        match = self.re_labop2.search(p_line)
        if match:
            self.is_valid = True
            g = match.groups()
            self.label    = g[0].upper()
            self.opcode   = g[1].upper()
            self.operand1 = g[2].upper()
            self.operand2 = g[3].upper()
            return

        # Is this a 2 operand, no label line?
        match = self.re_op2.search(p_line)
        if match:
            self.is_valid = True
            g = match.groups()
            self.opcode   = g[0].upper()
            self.operand1 = g[1].upper()
            self.operand2 = g[2].upper()
            return

       # Opcode only line?
        match = self.re_opcode.search(p_line)
        if match:
            self.is_valid = True
            g = match.groups()
            self.opcode = g[0].upper()
            return

        # Label + opcode + operand line?
        match = self.re_labop1.search(p_line)
        if match:
            self.is_valid = True
            g = match.groups()
            self.label    = g[0].upper()
            self.opcode   = g[1].upper()
            self.operand1 = g[2].upper()
            return

        # Opcode + one operand?
        match = self.re_op1.search(p_line)
        if match:
            self.is_valid = True
            g = match.groups()
            self.opcode   = g[0].upper()
            self.operand1 = g[1].upper()
            return

        raise ParseError(self.line_number,
                         """Line can't be parsed into label, opcode,
                         operand fields""")


    def __validate(self):
        """ Check if the fields are actually valid labels, opcodes, etc.
        Provide helpful error messages where possible.
        """
        if self.label:
            self.__validate_label(self.label)

        if self.opcode:
            match = self.re_pseudo.search(self.opcode)
            if match:
                self.__validate_pseudo_opcode(self.opcode)
            else:
                self.__validate_opcode(self.opcode)

        if self.label or self.opcode:
            self.__validate_memory_address()


    def __validate_opcode(self, opcode):
        """ An opcode must be a valid mnemonic.
        Check if the opcode has the proper number of operands.
        Then check if the operands are of the proper type.
        """
        if OpcodeInfo.invalid_opcode(opcode):
            raise SyntaxError(self.line_number,
                              "Invalid opcode (%s)" % (opcode, ))
        elif OpcodeInfo.num_operands(opcode) == 0:
            if self.operand1:
                raise SyntaxError(self.line_number,
                                  "The " + opcode + " instruction requires " +
                                  "no operands, but you provided one (" +
                                  self.operand1 + ")")
        elif OpcodeInfo.num_operands(opcode) == 1:
            if self.operand2:
                raise SyntaxError(self.line_number,
                                  "The " + opcode + " instruction requires " +
                                  "one operand, but you provided two (" +
                                  self.operand1 + " and " + self.operand2 + ")")
            if not self.operand1:
                raise SyntaxError(self.line_number,
                                  "The " + opcode + " instruction requires " +
                                  "one operand, but you provided none.")
            self.__validate_operand_type(1)
        else:
            if not self.operand1:
                raise SyntaxError(self.line_number,
                                  "The " + opcode + " instruction requires " +
                                  "two operands, but you provided none.")
            if not self.operand2:
                raise SyntaxError(self.line_number,
                                  "The " + opcode + " instruction requires " +
                                  "two operands, but you provided one (" +
                                  self.operand1 + ")")
            self.__validate_operand_type(1)
            self.__validate_operand_type(2)

    def __validate_label(self, label):
        """ A label is valid if it matches the validation regular expression
        (which checks that it is one or more alphanumeric or _ characters).
        It also must not have already been declared (i.e. placed in the symbol
        table).  A valid label will be placed in the symbol table by this
        function.
        """
        match = self.re_vallabel.search(label)
        if match:
            SymbolTable.add_label(label, self.mem_address, self.line_number)
        else:
            raise SyntaxError(self.line_number, "Invalid label (" + label +
                              ").  Labels may only consist of alphanumeric " +
                              "or underbar characters.")

    def __validate_pseudo_opcode(self, p_opcode):
        """ Check the Pseudo operation has the required number
        and type of operands
        """
        #EQU: requires a label and a single, numeric (i.e. HEX number) operand
        if p_opcode == ".EQU":
            if not self.label:
                raise SyntaxError(self.line_number,
                                  "A .EQU pseudo-operation requires a " +
                                  "label.  You provided none.")
            if self.operand2:
                raise SyntaxError(self.line_number,
                                  "A .EQU pseudo-operation requires a " +
                                  "single operand, but you provided two (" +
                                  self.operand1 + " and " + self.operand2 +
                                  ")")
            if not self.operand1:
                raise SyntaxError(self.line_number,
                                  "A .EQU pseudo-operation requires one " +
                                  "operand, but you provided none.")
            match = self.re_valop_hex.search(self.operand1)
            if not match:
                raise SyntaxError(self.line_number,
                                  "A .EQU pseudo-operation requires the " +
                                  "operand be a hex value (like $01FF), but " +
                                  "you provided " + self.operand1)

        #DW: optional label.  Required zero or one operand (numeric).
        elif p_opcode == ".DW":
            if self.operand2:
                raise SyntaxError(self.line_number,
                                  "A .DW pseudo-operation requires zero " +
                                  "or one operands, but you provided two (" +
                                  self.operand1 + " and " + self.operand2 +
                                  ")")
            if self.operand1:
                match = self.re_valop_hex.search(self.operand1)
                if not match:
                    raise SyntaxError(self.line_number,
                                      "A .DW pseudo-operation requires the " +
                                      "operand be a hex value (like $01FF), " +
                                      "but you provided " + self.operand1)

        #ORG: no label allowed. Requires a single, numeric operand
        elif p_opcode == ".ORG":
            if self.label:
                raise SyntaxError(self.line_number,
                                  "A .ORG pseudo-operation is not allowed " +
                                  "to have a label.  You provided one (" +
                                  self.label + ").")
            if self.operand2:
                raise SyntaxError(self.line_number,
                                  "A .ORG pseudo-operation requires a " +
                                  "single operand, but you provided two (" +
                                  self.operand1 + " and " + self.operand2 +
                                  ")")
            if not self.operand1:
                raise SyntaxError(self.line_number,
                                  "A .ORG pseudo-operation requires one " +
                                  "operand, but you provided none.")
            match = self.re_valop_hex.search(self.operand1)
            if not match:
                raise SyntaxError(self.line_number,
                                  "A .ORG pseudo-operation requires the " +
                                  "operand be a hex value (like $01FF), but " +
                                  "you provided " + self.operand1)
        self.is_pseudo_operation = True

    def __validate_operand_type(self, operand_number):
        """ Check that the given operand number (i.e. first or second)
        is of the proper type.  Check against the validation regular
        expressions.
        """
        if operand_number == 1:
            operand = self.operand1
            required_type = OpcodeInfo.operand1_type(self.opcode)
            operand_string = "first"
        else:
            operand = self.operand2
            required_type = OpcodeInfo.operand2_type(self.opcode)
            operand_string = "second"

        if required_type == 'register':
            match = self.re_valop_reg.search(operand)
            if not match:
                raise SyntaxError(self.line_number,
                                  "A " + self.opcode + " instruction " +
                                  "requires the " + operand_string +
                                  " operand be a register (R0-R7), " +
                                  "but you provided " + operand)
        else:
            match = self.re_valop_num.search(operand)
            if not match:
                raise SyntaxError(self.line_number,
                                  "A " + self.opcode + " instruction " +
                                  "requires the " + operand_string +
                                  " operand be a label or hex value (like" +
                                  " $01FF), but you provided " + operand)
            match = self.re_valop_reg.search(operand)
            if match:
                raise SyntaxError(self.line_number,
                                  "A " + self.opcode + " statement " +
                                  "requires the " + operand_string +
                                  " operand not be a register, " +
                                  "but you provided " + operand)


    def __validate_memory_address(self):
        """ Check that a memory address has already been initialized
        (via .ORG) prior to this statement.  This function will be
        called if the validating line has an opcode or a label.
        """
        if self.opcode == ".ORG":
            return
        if self.opcode == ".EQU":
            return
        if self.mem_address == None:
            raise SyntaxError(self.line_number,
                              "You must use .ORG to initialize a memory " +
                              "section before any line with a label or " +
                              "opcode")

    def next_mem_address(self):
        """ Calculate what the memory address of the next line will be,
        based on the starting address for this line, and the size of the
        machine code for this line (if any).
        """
        if self.opcode == ".ORG":
            return int(self.operand1[1:], 16)  #operand1 hex string to integer
        elif self.mem_address == None:     # beginning of a file, before an ORG
            return None
        elif self.opcode == ".EQU":
            return self.mem_address     # .EQU takes no memory
        elif self.opcode == ".DW":
            return self.mem_address + 1 # .DW always takes up one word
        elif self.opcode:
            return self.mem_address + OpcodeInfo.operation_size(self.opcode)
        else:
            return self.mem_address

    def assemble(self):
        ''' Figure out what the machine words are for this instruction.'''
        if not self.opcode:
            return
        elif self.opcode == '.DW':
            self.word1 = int(self.operand1[1:], 16)
            return
        elif self.opcode == '.EQU' or self.opcode == '.ORG':
            return
        else:
            mach_code = (OpcodeInfo.encoding_is(self.opcode) +
                         self.__assemble_field(OpcodeInfo.field1_is(self.opcode)) +
                         self.__assemble_field(OpcodeInfo.field2_is(self.opcode))
                        )
            self.word1 = int(mach_code, 2)
        if OpcodeInfo.format_is_long(self.opcode):
            self.word2 = self.__assemble_long(self.opcode)

    def __assemble_register(self, reg_string):
        """ Given a string like R4, return the 3 character binary string
        representing the register number (i.e. '100').  This value will be
        used when assembling the register fields of the instruction.
        """
        if reg_string == 'R0':
            return '000'
        if reg_string == 'R1':
            return '001'
        if reg_string == 'R2':
            return '010'
        if reg_string == 'R3':
            return '011'
        if reg_string == 'R4':
            return '100'
        if reg_string == 'R5':
            return '101'
        if reg_string == 'R6':
            return '110'
        if reg_string == 'R7':
            return '111'
        raise ValueError("DEBUG: Invalid register string: " + reg_string)

    def __assemble_field(self, field_string):
        """ Given a string representing what goes in a field
        (i.e. zero, op1, op2) return the binary string for that field.
        """
        if field_string == 'zero':
           return '000'
        elif field_string == 'op1':
           return self.__assemble_register(self.operand1)
        elif field_string == 'op2':
           return self.__assemble_register(self.operand2)
        raise ValueError("DEBUG: Invalid field string: " + field_string)

    def __assemble_long(self, opcode):
        """ Return the integer value of what the machine code is for
        the second word of a long format instruction.
        """
        if OpcodeInfo.field3_is(opcode) == 'op1':
          val = self.operand1
        elif OpcodeInfo.field3_is(opcode) == 'op2':
          val = self.operand2
        else:
          raise ValueError("DEBUG: Invalid field3 in opcode_info for " + opcode)

        match = self.re_valop_hex.search(val)
        if match:
            return int(val[1:], 16) # The operand is a hex string, so int it.
        else:
            return SymbolTable.lookup_label(val, self.line_number)

class SymbolTable:

    table = {}

    @classmethod
    def add_label(cls, label, mem_address, line_number):
        if label in cls.table:
            raise SyntaxError(line_number, "Duplicate label (" + label +
                              ").  Label has already been declared on a " +
                              "previous line.")
        cls.table[label] = mem_address

    @classmethod
    def lookup_label(cls, label, line_number):
        """ returns mem_address """
        if label in cls.table:
            return cls.table[label]
        else:
            raise SyntaxError(line_number,
                              "The label " + label +
                              " has not been defined anywhere.")

    @classmethod
    def clear(cls):
        """
        Deletes all symbols in the symbol table.  Primarily used for
        testing.  Not anticipated to be used in normal assembly.
        """
        cls.table = {}

    @classmethod
    def printable_string(cls):
        if not cls.table:
            return "Symbol table is empty"
        else:
            max_len = 0
            long_label = False

            for key in cls.table.keys():
                if len(key) > max_len:
                    max_len = len(key)

            if max_len > 40:
                max_len = 40
                long_label = True

            if max_len < 7:
                max_len = 7

            ret_val = "{0:^{1}}  Address\n{2}  -------\n".format('Label',
                      max_len, '-' * max_len)

            for label, address in sorted(cls.table.items()):
                printable_label = label
                if len(label) > 40:
                    printable_label = label[:40]
                ret_val += "{0:<{1}}   ${2:0>4X}\n".format(
                           printable_label, max_len, address)
            if long_label:
              ret_val += "Only 40 characters of long labels are shown. \n"
              ret_val += "Remaining characters are still significant.\n"
            return ret_val


# Command line processing
# -h, --help	Provide short help text and usage information
# -m <filename>	Use the specified filename for the memory.hex file
# -l <filename>	Use the specified filename for the .list file
# -s [<filename>]	Output the symbol list as <basename>.sym or <filename> if specified
# -	Send .list output to stdout (for piping into sim240) rather than a file.
# -version	Print the version of as240 and quit.
# If syntax errors are encountered, up to 5 will be printed on SYSERR.  The
#    the assembler will be terminated and the number of syntax errors set as
#    the exit code

def parse_command_line():
    """Deep and thorough parsing of command line options.

    Do all command line processing.  Read the ASM file.
    Returns:
        asm_data : A string with the entire contents of the assembly file
        file_list, file_mem, file_sym : file objects for the output files
    """
    usage = "usage: %prog [options] ASM_FILE"
    program_version = "2.0"  # Perl version went to 1.5 or so

    parser = OptionParser(usage=usage, version="%prog " + program_version)

    parser.add_option("-m", "--mfile",
                      dest="mfile",
                      metavar = "MEM_FILE",
                      help="Use the specified filename for the memory.hex file.  \
                            Note: no extension will be added",
                      default="memory.hex")
    parser.add_option("-l", "--listfile",
                      dest="lfile",
                      metavar = "LIST_FILE",
                      help="Output list format to LIST_FILE",
                      default=None)
    parser.add_option("-s", "--symbolfile", "--symfile",
                      dest="sfile",
                      metavar = "SYM_FILE",
                      help="Output symbol list to SYM_FILE")
    parser.add_option("-o",
                      dest="output_to_stdout",
                      action="store_true",
                      help="list file will be output to STDOUT.  \
                            No other files created",
                      default=False)

    (options, args) = parser.parse_args()
    if len(args) > 1:
        parser.error("incorrect number of arguments")
    if (len(args) == 0) and not (options.output_to_stdout):
        parser.error("incorrect number of arguments")

    if '.' in args[0]:
        options.afile = args[0]
        options.basefile = args[0][:args[0].rfind('.')]
    else:
        options.afile = args[0] + ".asm"
        options.basefile = args[0]

    if not options.lfile :
        options.lfile = options.basefile + ".list"

    try:
        file_asm = open(options.afile, 'r')
    except IOError:
        parser.error("ASM_FILE does not exist")

    if (options.output_to_stdout):
        file_list = sys.stdout
        if options.sfile:
            file_sym = open(options.sfile, 'w')
        else:
            file_sym = open('/dev/null', 'w')
        if options.mfile:
            file_mem = open(options.mfile, 'w')
        else:
            file_mem = open('/dev/null', 'w')
    else:
        file_list = open(options.lfile, 'w')
        file_mem = open(options.mfile, 'w');
        if options.sfile :
            file_sym = open(options.sfile, 'w')
        else:
            file_sym = open('/dev/null', 'w')

    return [file_asm, file_list, file_mem, file_sym]

def main():

    (file_asm, file_list, file_mem, file_sym) =  parse_command_line()

    line_number = 1
    mem_address = None  # In case there is no .ORG statement, need to detect
    code = []
    syntax_errors = 0
    MAX_SYNTAX_ERRORS = 5

    # First pass, assemble as much as possible.  Build symbol table
    for line in file_asm:
        try:
            a = AsmLine(line, line_number, mem_address)
        except SyntaxError, se:
            syntax_errors += 1
            print(se, file=sys.stderr)
            if syntax_errors > MAX_SYNTAX_ERRORS:
                sys.exit(syntax_errors)

        code.append(a)
        line_number += 1
        mem_address = a.next_mem_address()

    if syntax_errors > 0:
        sys.exit(syntax_errors)

    file_asm.close()
    # Print the symbol table
    print(SymbolTable.printable_string(), file=file_sym)
    file_sym.close()

    if syntax_errors == 0:
        print("addr data  label   opcode  operands", file=file_list)
        print("---- ----  -----   ------  --------", file=file_list)

        for c in code:
            c.assemble()
            s = str(c)
            if s != "":
                print(s, file=file_list)
                print(c.mem_str(), file=file_mem)

    file_list.close()
    file_mem.close()

if __name__ == '__main__':
    sys.dont_write_bytecode = True;
    main()
else:
    sys.dont_write_bytecode = True;
