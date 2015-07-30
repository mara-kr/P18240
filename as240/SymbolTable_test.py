#! /usr/bin/python
"""Unit test for SymbolTable"""

import unittest
from as240 import SymbolTable
from as240 import SyntaxError

class ST_test(unittest.TestCase):
    
    def testAddingLabel(self):
        """Adding a new label will succeed. """
        labels = ['Hi', 'Label', 'LongLabel_really_really_long']
        addr = 1200
        line = 1
        for l in labels:
            SymbolTable.add_label(l, addr, line)
            addr += 1400
            line += 1
        
    def testRetrievingLabel(self):
        """Retriving a defined label will return the stored value."""
        SymbolTable.clear()
        labels = ['Hi', 'Label', 'LongLabel_really_really_long']
        addr = 1200
        line = 1
        for l in labels:
            SymbolTable.add_label(l, addr, line)
            addr += 1400
            line += 1

        addr = 1200
        line = 1
        for l in labels:
            a = SymbolTable.lookup_label(l, line)
            self.assertEqual(a, addr)
            addr += 1400
            line += 1
        
    def testBadAdd(self):
        """ Adding an already defined label will generate a SyntaxError."""
        labels = []
        for x in dir(int):
            labels.append(x.replace('_',''))  # just a source of strings
        addr = 2000
        line = 1
        for l in labels:
            SymbolTable.add_label(l, addr, line)
            addr += 100
            line += 1
            self.assertRaises(SyntaxError, SymbolTable.add_label, l, addr, line)

    def testBadRetrieval(self):
        """ Retrieving an undefined label will raise a SyntaxError. """
        labels = ['Sane', 'Insane', 'M', '43', '18_240']
        line = 1
        for l in labels:
            self.assertRaises(SyntaxError, SymbolTable.lookup_label, l, line)
            
    def testPrintingEmpty(self):
        """ An empty symbol table, when printed, will return empty message."""
        SymbolTable.clear()
        s = SymbolTable.printable_string()
        self.assertEqual(s, 'Symbol table is empty')
        
    def testPrintingNormal(self):
        """ A symbol table, with normal sized labels, gets printed properly."""
        SymbolTable.clear()
        SymbolTable.add_label("STARTING", 1200, 1)
        SymbolTable.add_label("ENDINGPT", 1400, 2)
        s = SymbolTable.printable_string()
        expect = (" Label    Address\n"
                  "--------  -------\n"
                  "ENDINGPT   $0578\n"
                  "STARTING   $04B0\n")
        self.assertEqual(s, expect)
        
    def testPrintingLong(self):
        """ 
        A symbol table with labels > 40 chars, gets printed truncated,
        including the ending message about significance of labels.
        """
        SymbolTable.clear()
        SymbolTable.add_label("ALongLongLongVeryLongExtremelyQuiteLongLabel", 
                              1200, 1)
        SymbolTable.add_label("AnotherLongLongLongVeryLongExtremelyQuiteLongLabel", 
                              1400, 2)
        SymbolTable.add_label("ALabelThatIsVeryVeryVeryVeryLongWithSameFirstCharacters", 
                              1600, 3)
        SymbolTable.add_label("ALabelThatIsVeryVeryVeryVeryLongWithSameFirstCharactersAsAnotherLabel", 
                              1800, 4)
        s = SymbolTable.printable_string()
                  #1234567890123456789012345678901234567890
        expect = ("                 Label                    Address\n"
                  "----------------------------------------  -------\n"
                  "ALabelThatIsVeryVeryVeryVeryLongWithSame   $0640\n"
                  "ALabelThatIsVeryVeryVeryVeryLongWithSame   $0708\n"
                  "ALongLongLongVeryLongExtremelyQuiteLongL   $04B0\n"
                  "AnotherLongLongLongVeryLongExtremelyQuit   $0578\n"
                  "Only 40 characters of long labels are shown. \n"
                  "Remaining characters are still significant.\n")
        self.assertEqual(s, expect)
        
        
            
if __name__ == "__main__":
    unittest.main()            