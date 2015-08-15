module sevenSegmentDigit_top;
    logic [6:0] segment;
    logic [3:0] bcd;
    logic blank;

    sevenSegmentDigit d(.*);
    sevenSegmentDigit_tester t(.*);

endmodule: sevenSegmentDigit_top
