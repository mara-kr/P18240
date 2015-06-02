/*
 * File: datapath.v
 * Created: 4/5/1998
 * Modules contained: datapath
 * 
 * Changelog:
 * 23 Oct 2009: Separated paths.v into datapath.v and controlpath.v
 * 17 Nov 2009: Minor updates to facilitate synthesis (mcbender)
 * 13 Oct 2010: Updated always to always_comb and always_ff.Renamed to.sv(abeera) 
 * 17 Oct 2010: Updated to use enums instead of define's (iclanton)
 * 24 Oct 2010: Updated to use stuct (abeera)
 * 9  Nov 2010: Slightly modified variable names (abeera)
 * 25 Apr 2013: Changed newMDR to tri (mromanko) 
 */

`include "constants.sv"
 
/* 
 * module datapath
 *
 * This is the datapath for the p18240.  Mainly just instantiates stuff
 * in modules.v.
 */
module datapath (
   output [15:0] ir,
   output [15:0] sp,
   output [3:0]  condCodes,
   output [15:0] aluSrcA,
   output [15:0] aluSrcB,
   output [127:0] viewReg, //register for viewing in debugging
   output [15:0] aluResult,
   output [15:0] pc,
   output [15:0] memAddr,
   output [15:0] MDRout,  // output of datapath just for viewing
   inout  [15:0] dataBus,
   output [2:0]  regSelA,
   output [2:0]  regSelB,
   input controlPts  cPts,
   input         clock,
   input         reset_L);

   logic [15:0] regA, regB;
   logic [15:0] memOut;
   logic [3:0]  newCC;
   logic loadReg_L, loadSP_L, loadPC_L, loadMDR_L, writeMD_L, loadMAR_L, loadIR_L;
   tri [15:0] newMDR;
   
   // Assign wires
   assign loadMDR_L = writeMD_L & cPts.re_L;
   assign regSelA = ir[5:3];
   assign regSelB = ir[2:0];
   
   // Instantiate the modules that we need:
   reg_file rfile(
           .outA(regA),
           .outB(regB),
           .outView(viewReg),
           .in(aluResult),
           .load_L(loadReg_L),
           .selA(ir[5:3]),
           .selB(ir[2:0]),
           .clock(clock),
           .reset_L(reset_L));
   
   tridrive #(.WIDTH(16)) a(.data(aluResult), .bus(newMDR), .en_L(writeMD_L)),
                          b(.data(dataBus), .bus(newMDR), .en_L(cPts.re_L)),
                          c(.data(MDRout), .bus(dataBus), .en_L(cPts.we_L));
   
   mux4to1 #(.WIDTH(16)) MuxA(.inA(regA), .inB(sp), .inC(pc), .inD(MDRout),
                              .out(aluSrcA), .sel(cPts.srcA)), /////////cPts[9:8]
                         MuxB(.inA(regB), .inB(sp), .inC(pc), .inD(MDRout),
                              .out(aluSrcB), .sel(cPts.srcB));//////////cPts[7:6]

   alu alu_dp(.out(aluResult), .condCodes(newCC), .inA(aluSrcA), .inB(aluSrcB),
              .opcode(cPts.alu_op));
   
   demux #(.OUT_WIDTH(6), .IN_WIDTH(3), .DEFAULT(1))
         reg_load_decoder (.in(1'b0), .sel(cPts.dest),
                .out({loadIR_L, loadMAR_L, writeMD_L, loadPC_L, loadSP_L, loadReg_L}));
   
   register #(.WIDTH(16)) pcReg(     .out(pc), .in(aluResult), .load_L(loadPC_L),
                                     .clock(clock), .reset_L(reset_L));
   register #(.WIDTH(16)) memDataReg(.out(MDRout), .in(newMDR), .load_L(loadMDR_L),
                                     .clock(clock), .reset_L(reset_L));
   register #(.WIDTH(16)) memAddrReg(.out(memAddr), .in(aluResult), .load_L(loadMAR_L),
                                     .clock(clock), .reset_L(reset_L));
   register #(.WIDTH(16)) instrReg(  .out(ir), .in(aluResult), .load_L(loadIR_L),
                                     .clock(clock), .reset_L(reset_L));
   register #(.WIDTH(16)) spReg(     .out(sp), .in(aluResult), .load_L(loadSP_L),
                                     .clock(clock), .reset_L(reset_L));
   
   register #(.WIDTH(4)) condCodeReg(.out(condCodes), .in(newCC), .load_L(cPts.lcc_L),
                                     .clock(clock), .reset_L(reset_L));
   
endmodule 
