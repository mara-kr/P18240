module sevenSegmentDigit
    (output logic [6:0] segment,
     input  logic [3:0] bcd,
     input  logic blank);

     always_comb
       if (blank==1)
         segment = 7'b111_1111;
       else
         case (bcd)
           4'd0 : segment = 7'b100_0000;
           4'd1 : segment = 7'b111_1001;
           4'd2 : segment = 7'b010_0100;
           4'd3 : segment = 7'b011_0000;
           4'd4 : segment = 7'b001_1001;
           4'd5 : segment = 7'b001_0010;
           4'd6 : segment = 7'b000_0010;
           4'd7 : segment = 7'b111_1000;
           4'd8 : segment = 7'b000_0000;
           4'd9 : segment = 7'b001_1000;
           default: segment = 7'bxxx_xxxx;
         endcase
endmodule: sevenSegmentDigit

/*
To autolabify something, add checks on values from the DUT, in the format:
    assert (condition) else $error(autograder message);
*/
module sevenSegmentDigit_tester
    (input  logic [6:0] segment,
     output logic [3:0] bcd,
     output logic blank);

    initial begin
        $display("#![p1, 10]");
     // $monitor($time,,"bcd = %b, blank = %b, segment = %b",bcd,blank,segment);
         bcd = 4'd0; blank = 0;
      #5 assert (segment == 7'b100_0000) else $error("#![p1, -=2]\n");
      #5 bcd = 4'd0; blank = 1;
      #5 assert (segment == 7'b100_0000) else $error("#![p1, -=2]\n");
      #5 bcd = 4'd8; blank = 0;
      #5 assert (segment == 7'd0) else $error("#![p1, -=2]\n");
      #5 bcd = 4'd8; blank = 1;
      #5 assert (segment == 7'b111_1111) else $error("#![p1, -=2]\n");
      #5 bcd = 4'd5; blank = 0;
      #5 assert (segment == 7'b001_0010) else $error("#![p1, -=2]\n");
      $display("#$Done grading");
      #5 bcd = 4'd3; blank = 0;
    end
endmodule: sevenSegmentDigit_tester
