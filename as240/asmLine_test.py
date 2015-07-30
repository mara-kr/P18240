#! /usr/bin/python
"""Unit test for as240 stuff"""

import unittest
from asmLine import AsmLine
from as240_exceptions import ParseError
from as240_exceptions import SyntaxError

class ParseGoodLines(unittest.TestCase):
    
    def testBlankLine(self):
        """A blank line should have no label, opcode, operands"""
        a = AsmLine("", 0, 0)
        self.assertIsNone(a.label)
        self.assertIsNone(a.opcode)
        self.assertIsNone(a.operand1)
        self.assertIsNone(a.operand2)
        self.assertTrue(a.is_valid)

    def testWhitespaceOnlyLine(self):
        """ A line with only whitespace should have no label, opcode or operands"""
        a = AsmLine("   \t", 0, 0)
        self.assertIsNone(a.label)
        self.assertIsNone(a.opcode)
        self.assertIsNone(a.operand1)
        self.assertIsNone(a.operand2)
        self.assertTrue(a.is_valid)

    def testLabelOnlyLine(self):
        """A line starting with some alphanumeric characters is a label"""
        a = AsmLine("ABC", 0, 0)
        self.assertEqual(a.label, 'ABC')
        self.assertIsNone(a.opcode)
        self.assertIsNone(a.operand1)
        self.assertIsNone(a.operand2)
        self.assertTrue(a.is_valid)

    def testLabelWhitespaceLine(self):
        """A line starting with some alphanumeric characters followed by whitespace is a label"""
        a = AsmLine("DEF  \t  ", 0, 0)
        self.assertEqual(a.label, 'DEF')
        self.assertIsNone(a.opcode)
        self.assertIsNone(a.operand1)
        self.assertIsNone(a.operand2)
        self.assertTrue(a.is_valid)
    
    def testLabelIsCaseInsensitive(self):
        """A label will always be considered uppercase"""
        a = AsmLine("hijklmnop  \t  ", 0, 0)
        self.assertEqual(a.label, 'HIJKLMNOP')
        self.assertIsNone(a.opcode)
        self.assertIsNone(a.operand1)
        self.assertIsNone(a.operand2)
        self.assertTrue(a.is_valid)

    def testLabelOpcodeLine(self):
        """A line starting with a label and an opcode is parsed properly"""
        a = AsmLine("qrstuv  \t  STOP", 0, 0)
        self.assertEqual(a.label, 'QRSTUV')
        self.assertEqual(a.opcode, 'STOP')
        self.assertIsNone(a.operand1)
        self.assertIsNone(a.operand2)
        self.assertTrue(a.is_valid)
        
    def testLabelSpaceOpcodeLine(self):
        """There can be as little as a single space between label and opcode"""
        a = AsmLine("wxyz RTN", 0, 0)
        self.assertEqual(a.label, 'WXYZ')
        self.assertEqual(a.opcode, 'RTN')
        self.assertIsNone(a.operand1)
        self.assertIsNone(a.operand2)
        self.assertTrue(a.is_valid)
        
    def testOpcodeIsCaseInsensitive(self):
        """An opcode will always be considered uppercase"""
        a = AsmLine("AB  \t  sToP", 0, 0)
        self.assertEqual(a.label, 'AB')
        self.assertEqual(a.opcode, 'STOP')
        self.assertIsNone(a.operand1)
        self.assertIsNone(a.operand2)
        self.assertTrue(a.is_valid)
        
    def testOpcodeAlone(self):
        """A line starting with whitespace, followed by text, is regarded as an opcode"""
        a = AsmLine("\tRTN", 0, 0)
        self.assertIsNone(a.label)
        self.assertEqual(a.opcode, 'RTN')
        self.assertIsNone(a.operand1)
        self.assertIsNone(a.operand2)
        self.assertTrue(a.is_valid)
        
    def testPseudoOpcodeAlone(self):
        """A line starting with whitespace, followed by .text, is regarded as an opcode"""
        a = AsmLine("       .DW", 0, 0)
        self.assertIsNone(a.label)
        self.assertEqual(a.opcode, '.DW')
        self.assertIsNone(a.operand1)
        self.assertIsNone(a.operand2)
        self.assertTrue(a.is_valid)
        
    def testOpcodeOperand(self):
        """A line with whitespace, text, whitespace, text is opcode/operand"""
        a = AsmLine("    PUSH R3", 0, 0)
        self.assertIsNone(a.label)
        self.assertEqual(a.opcode, 'PUSH')
        self.assertEqual(a.operand1, 'R3')
        self.assertIsNone(a.operand2)
        self.assertTrue(a.is_valid)
        
    def testOperand1AsRegister(self):
        """A line with whitespace, text, whitespace, R{0-7} is opcode/operand"""
        for r in ['R0', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7'] :
            a = AsmLine("    ASHR "+ r, 0, 0)
            self.assertIsNone(a.label)
            self.assertEqual(a.opcode, 'ASHR')
            self.assertEqual(a.operand1, r)
            self.assertIsNone(a.operand2)
            self.assertTrue(a.is_valid)

    def testOperand1AsHexNum(self):
        """A line with whitespace, text, whitespace, $XX is opcode/operand"""
        for hex_num in ['$0', '$10', '$ABC', '$01FF', '$FFFF', '$0000', '$0001'] :
            a = AsmLine("    BRA "+ hex_num, 0, 0)
            self.assertIsNone(a.label)
            self.assertEqual(a.opcode, 'BRA')
            self.assertEqual(a.operand1, hex_num)
            self.assertIsNone(a.operand2)
            self.assertTrue(a.is_valid)    
        
    def testPseudoOpcodeOperand(self):
        """A line with whitespace, .text, whitespace, text is opcode/operand"""
        for hex_num in ['$0', '$10', '$ABC', '$01FF', '$FFFF', '$0000', '$0001'] :
            a = AsmLine("    .ORG " + hex_num, 0, 0)
            self.assertIsNone(a.label)
            self.assertEqual(a.opcode, '.ORG')
            self.assertEqual(a.operand1, hex_num)
            self.assertIsNone(a.operand2)
            self.assertTrue(a.is_valid)

    def testOpcode2Operands(self):
        """A line with whitespace, text, whitespace, text, comma text is opcode/operand/operand"""
        a = AsmLine("    LDI R4,$1200", 0, 0)
        self.assertIsNone(a.label)
        self.assertEqual(a.opcode, 'LDI')
        self.assertEqual(a.operand1, 'R4')
        self.assertEqual(a.operand2, '$1200')
        self.assertTrue(a.is_valid)

    def testOpcode2OperandsWhitespace(self):
        """A line with 2 operands can have whitespace before the comma"""
        a = AsmLine("    CMI R0\t,$1987", 0, 0)
        self.assertIsNone(a.label)
        self.assertEqual(a.opcode, 'CMI')
        self.assertEqual(a.operand1, 'R0')
        self.assertEqual(a.operand2, '$1987')
        self.assertTrue(a.is_valid)
        
    def testOpcode2OperandsWhitespace2(self):
        """A line with 2 operands can have whitespace after the comma"""
        a = AsmLine("    ADD R3,\tR4", 0, 0)
        self.assertIsNone(a.label)
        self.assertEqual(a.opcode, 'ADD')
        self.assertEqual(a.operand1, 'R3')
        self.assertEqual(a.operand2, 'R4')
        self.assertTrue(a.is_valid)
        
    def testOpcode2OperandsWhitespace3(self):
        """A line with 2 operands can have whitespace before and after the comma"""
        a = AsmLine("    SUB R5  \t,     R2", 0, 0)
        self.assertIsNone(a.label)
        self.assertEqual(a.opcode, 'SUB')
        self.assertEqual(a.operand1, 'R5')
        self.assertEqual(a.operand2, 'R2')
        self.assertTrue(a.is_valid)

class ParseBadLines(unittest.TestCase):

    def testBadNumFields(self):
        """Lines with more than 4 fields fail parsing"""
        self.assertRaises(ParseError, AsmLine, "Label  PUSH Operand , Operand2 ExtraField", 1, 0)

    def testBadLabel(self):
        """Labels are Alphanumeric (and underbar) only"""
        self.assertRaises(SyntaxError, AsmLine, "L:abel STOP", 1, 0)

    def testBadOpcode(self):
        """Opcodes are Alpha only"""
        self.assertRaises(SyntaxError, AsmLine, "Label  LDA3 Operand1 , Operand2", 2, 0)

    def testBadPseudoOpcode(self):
        """Opcodes can't have period except at beginning """
        self.assertRaises(SyntaxError, AsmLine, "Label  ORG. Operand1 , Operand2", 3, 0)

    def testBadOperand1(self):
        """Operand1 can only have $ in starting position"""
        self.assertRaises(SyntaxError, AsmLine, "Label  POP AF$00 , Operand2", 4, 0)

    def testBadOperand1_hex(self):
        """Operand1, if starting with a $, can only have hex digits following"""
        self.assertRaises(SyntaxError, AsmLine, "Label  BRA $AG99 , Operand2", 5, 0)

    def testBadOperand1_hex2(self):
        """Operand1 can't have two $ signs"""
        self.assertRaises(SyntaxError, AsmLine, "Label  ADD $$099 , Operand2", 6, 0)

    def testBadOperand1_hex3(self):
        """Operand1, if starting with a $, can only have a max of 4 digits following"""
        self.assertRaises(SyntaxError, AsmLine, "Label  SUB $DEAD1 , Operand2", 7, 0)

    def testBadOperand1_label(self):
        """Operand1, not starting with $, is AlphaNumeric only"""
        self.assertRaises(SyntaxError, AsmLine, "Label  LSHR Bad_Label , Operand2", 8, 0)

    def testBadOperand2(self):
        """Operand2 can only have $ in starting position"""
        self.assertRaises(SyntaxError, AsmLine, "Label  LSHL Operand1 , A$", 9, 0)

    def testBadOperand2_hex(self):
        """Operand2, if starting with a $, can only have hex digits following"""
        self.assertRaises(SyntaxError, AsmLine, "Label  LDA Operand1 , $049X", 10, 0)

    def testBadOperand2_hex2(self):
        """Operand2 can't have two $ signs"""
        self.assertRaises(SyntaxError, AsmLine, "Label  ASHR Operand1 , $$12", 11, 0)

    def testBadOperand2_hex3(self):
        """Operand2, if starting with a $, can only have a max of 4 digits following"""
        self.assertRaises(SyntaxError, AsmLine, "Label  ROR Operand1 , $01234", 12, 0)

    def testBadOperand2_label(self):
        """Operand2, not starting with $, is AlphaNumeric only"""
        self.assertRaises(SyntaxError, AsmLine, "Label  STOP Operand1 , Bad-Operand", 13, 0)

    def testBadOperandSeparator(self):
        """Operands must be separated by a comma"""
        self.assertRaises(ParseError, AsmLine, "Label  AND Operand1 Operand2", 14, 0)

    def testBadOperandSeparator2(self):
        """Operands must be separated by a comma, not a dash"""
        self.assertRaises(ParseError, AsmLine, "Label  AND Operand1 _ Operand2", 15, 0)

class ParseBadSemantics(unittest.TestCase):

    def rotate_list(self, l):
        el = l[0]
        del(l[0])
        l.append(el)
        return el

    def test1RegOperand(self):
        """Instructions with one register operand cannot have label or hex num for operand.
             They can only have register names for operands."""
        alu1ops = ['ASHR', 'DECR', 'INCR', 'LDSP', 'LSHL', 'LSHR', 'NEG', 'NOT', 'POP', 'PUSH', 'ROL', 'STSP']
        labels = ['L_', 'ENDIT', '12Harry', 'Moses_and_Aaron']
        hexnums = ['$12', '$0', '$1', '$FFFF', '$00FF', '$1492']
        registers = ['R0', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7']
        for instr in alu1ops:
            label = self.rotate_list(labels)
            line = "  %s %s" % (instr, label)
            self.assertRaises(SyntaxError, AsmLine, line, 1, 1)
            hexnum = self.rotate_list(hexnums)
            line = "  %s %s" % (instr, hexnum)
            self.assertRaises(SyntaxError, AsmLine, line, 1, 1)
            register = self.rotate_list(registers)
            line = "  %s %s" % (instr, register)
            a = AsmLine(line, 1, 1)  # does not raise anything

    def test2RegOperands(self):
        """Instructions with two register operands cannot have label or hex num for operands.
             They can only have register names for operands."""
        alu2ops = ['ADD', 'AND', 'CMR', 'LDR', 'MOV', 'OR', 'STR', 'SUB', 'XOR']
        labels = ['L_', 'ENDIT', '12Harry', 'Moses_and_Aaron']
        hexnums = ['$12', '$0', '$1', '$FFFF', '$00FF', '$1492']
        registers = ['R0', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7']
        for instr in alu2ops:
            label = self.rotate_list(labels)
            register = self.rotate_list(registers)
            line = "  %s %s, %s" % (instr, label, register)
            self.assertRaises(SyntaxError, AsmLine, line, 1, 1)
            line = "  %s %s, %s" % (instr, register, label)
            self.assertRaises(SyntaxError, AsmLine, line, 1, 1)

            hexnum = self.rotate_list(hexnums)
            register = self.rotate_list(registers)
            line = "  %s %s, %s" % (instr, hexnum, register)
            self.assertRaises(SyntaxError, AsmLine, line, 1, 1)
            line = "  %s %s, %s" % (instr, register, hexnum)
            self.assertRaises(SyntaxError, AsmLine, line, 1, 1)

            hexnum = self.rotate_list(hexnums)
            label = self.rotate_list(labels)
            line = "  %s %s, %s" % (instr, hexnum, label)
            self.assertRaises(SyntaxError, AsmLine, line, 1, 1)
            line = "  %s %s, %s" % (instr, label, hexnum)
            self.assertRaises(SyntaxError, AsmLine, line, 1, 1)

            register1 = self.rotate_list(registers)
            register2 = self.rotate_list(registers)
            line = "  %s %s, %s" % (instr, register1, register2)
            a = AsmLine(line, 1, 1)  # does not raise anything
            
    def testImmediateOperand(self):
        """Instructions with one immediate operand (or addr) cannot have register for operands.
             They can only have label or hex value for operands."""
        ops = ['ADDSP', 'BRA', 'BRC', 'BRN', 'BRV', 'BRZ', 'JSR']
        labels = ['L_', 'ENDIT', '12Harry', 'Moses_and_Aaron']
        hexnums = ['$12', '$0', '$1', '$FFFF', '$00FF', '$1492']
        registers = ['R0', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7']
        for instr in ops:
            register = self.rotate_list(registers)
            line = "  %s %s" % (instr, register)
            self.assertRaises(SyntaxError, AsmLine, line, 1, 1)

            label = self.rotate_list(labels)
            line = "  %s %s" % (instr, label)
            a = AsmLine(line, 1, 1)  # does not raise anything

            hexnum = self.rotate_list(hexnums)
            line = "  %s %s" % (instr, hexnum)
            a = AsmLine(line, 1, 1)  # does not raise anything

    def testRegisterNumberOperands(self):
        """Instructions with two operands, the first a register and the second a number,
           cannot have register for operand2 nor number for operand1.
           They can only have register for operand1 and number (label or hex) for operand2."""
        ops = ['CMI', 'LDA', 'LDI', 'LDSF', 'STSF']
        labels = ['L_', 'ENDIT', '12Harry', 'Moses_and_Aaron']
        hexnums = ['$12', '$0', '$1', '$FFFF', '$00FF', '$1492']
        registers = ['R0', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7']
        for instr in ops:
            register = self.rotate_list(registers)
            label = self.rotate_list(labels)
            hexnum = self.rotate_list(hexnums)
            line = "  %s %s, %s" % (instr, label, register)
            self.assertRaises(SyntaxError, AsmLine, line, 1, 1)
            line = "  %s %s, %s" % (instr, hexnum, register)
            self.assertRaises(SyntaxError, AsmLine, line, 1, 1)

            line = "  %s %s, %s" % (instr, register, label)
            a = AsmLine(line, 1, 1)  # does not raise anything
            line = "  %s %s, %s" % (instr, register, hexnum)
            a = AsmLine(line, 1, 1)  # does not raise anything

    def testNumberRegisterOperands(self):
        """Instructions with two operands, the first a number and the second a register,
           cannot have register for operand1 nor number for operand2.
           They can only have register for operand2 and number (label or hex) for operand1."""
        ops = ['STA']
        labels = ['L_', 'ENDIT', '12Harry', 'Moses_and_Aaron']
        hexnums = ['$12', '$0', '$1', '$FFFF', '$00FF', '$1492']
        registers = ['R0', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7']
        for instr in ops:
            register = self.rotate_list(registers)
            label = self.rotate_list(labels)
            hexnum = self.rotate_list(hexnums)
            line = "  %s %s, %s" % (instr, register, label)
            self.assertRaises(SyntaxError, AsmLine, line, 1, 1)
            line = "  %s %s, %s" % (instr, register, hexnum)
            self.assertRaises(SyntaxError, AsmLine, line, 1, 1)

            line = "  %s %s, %s" % (instr, label, register)
            a = AsmLine(line, 1, 1)  # does not raise anything
            self.assertTrue(a.is_valid)
            line = "  %s %s, %s" % (instr, hexnum, register)
            a = AsmLine(line, 1, 1)  # does not raise anything
            self.assertTrue(a.is_valid)

    def testMemAddressNotSet(self):
        """No line with a label or opcode, with the exception of .ORG or .EQU, may be encountered
           prior to the memory address being set"""
        legal_lines = ['William .DW $1066', ' ADD R0, R2', ' ADDSP $3', ' AND R7, R6', ' ASHR R3']
        line_num = 1
        for ll in legal_lines:
            self.assertRaises(SyntaxError, AsmLine, ll, line_num, None)
            line_num += 1

    def testPseudoORG(self):
        """No label is allowed on a .ORG pseudo instruction line"""
        self.assertRaises(SyntaxError, AsmLine, "Label .ORG $1400", 1, 1)

    def testPseudoORG2(self):
        """Operand cannot be label on .ORG pseudo instruction line"""
        self.assertRaises(SyntaxError, AsmLine, "   .ORG Jones", 1, 1)
    
    def testPseudoORG2a(self):
        """Operand cannot be numeric label on .ORG pseudo instruction line"""
        self.assertRaises(SyntaxError, AsmLine, "   .ORG 1234", 1, 1)
    
    def testPseudoORG3(self):
        """Operand cannot be blank on .ORG pseudo instruction line"""
        self.assertRaises(SyntaxError, AsmLine, "   .ORG  ", 1, 1)
    
    def testPseudoORG4(self):
        """Cannot have 2 operands on .ORG pseudo instruction line"""
        self.assertRaises(SyntaxError, AsmLine, "   .ORG $1200, NoWay ", 1, 1)

    def testPseudoORG_Good(self):
        """The .ORG pseudo opcode must have a single operand (hexnum)"""
        a = AsmLine(' .ORG $1987' , 1, None)
        self.assertTrue(a.is_valid)
        
    def testPseudoDW(self):
        """Cannot have 2 operands on .DW pseudo instruction line"""
        self.assertRaises(SyntaxError, AsmLine, "   .DW $1000, NoWayJose ", 1, 1)
    
    def testPseudoDW2(self):
        """Cannot have register operands on .DW pseudo instruction line"""
        self.assertRaises(SyntaxError, AsmLine, "   .DW R2 ", 1, 1)

    def testPseudoDW3(self):
        """Operand cannot be label on .DW pseudo instruction line"""
        self.assertRaises(SyntaxError, AsmLine, "   .DW Jones", 1, 1)
    
    def testPseudoDW_Good(self):
        """The .DW pseudo opcode may have a label.  May or may not have a single operand"""
        legal_lines = ['Johnson .DW $15', 'Wilbur .DW', ' .DW', ' .DW $19']
        line_num = 1
        for ll in legal_lines:
            a = AsmLine(ll , line_num, 12)
            self.assertTrue(a.is_valid)

    def testPseudoEQU(self):
        """Cannot have 2 operands on .EQU pseudo instruction line"""
        self.assertRaises(SyntaxError, AsmLine, "Rosie .EQU $1FF0, NoWayJose ", 1, 1)
    
    def testPseudoEQU2(self):
        """Operand cannot be label on .EQU pseudo instruction line"""
        self.assertRaises(SyntaxError, AsmLine, "Timmy .EQU Jose ", 1, 1)
    
    def testPseudoEQU3(self):
        """Operand cannot be blank on .EQU pseudo instruction line"""
        self.assertRaises(SyntaxError, AsmLine, "   .EQU  ", 1, 1)
        
    def testPseudoEQU_Good(self):
        """The .EQU pseudo opcode must have a label and a single operand (hexnum)"""
        a = AsmLine('Jimmy .EQU $FFFF' , 1, 12)
        self.assertTrue(a.is_valid)

    def testDuplicateLabels(self):
        """A label may not be declared twice"""
        a = AsmLine('StarWars .EQU $FF00', 1, 14)
        self.assertRaises(SyntaxError, AsmLine, "StarWars LDA R2, $14", 2, 24)

    
if __name__ == "__main__":
    unittest.main()