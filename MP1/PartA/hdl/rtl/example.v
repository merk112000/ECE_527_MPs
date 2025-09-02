`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 01.09.2025 15:44:49
// Design Name: 
// Module Name: pA_rtl
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module pA_rtl(
    input  wire       clk_125,   // 125 MHz PL clock
    input  wire [1:0] sw,        // sw[0]=SW0, sw[1]=SW1
    output reg        ld4_b_n,   // LD4 blue (active-high)
    output reg        ld4_r_n,   // LD4 red  (keep OFF)
    output reg        ld4_g_n,   // LD4 green(keep OFF)
    output reg        ld5_b_n,   // LD5 blue (active-high)
    output reg        ld5_r_n,   // LD5 red  (keep OFF)
    output reg        ld5_g_n    // LD5 green(keep OFF)
);

    // 3-stage pipelines for SW0/SW1
    reg  [2:0] sr0 = 3'b000;
    reg  [2:0] sr1 = 3'b000;

    // Combinational "next" values (advance pipeline by one stage)
    wire [2:0] sr0_next = {sr0[1:0], sw[0]};
    wire [2:0] sr1_next = {sr1[1:0], sw[1]};

    // Combinational next LED values (use NEXT MSB so visible delay = 3)
    wire ld4_b_n_next = sr0_next[2];
    wire ld5_b_n_next = sr1_next[2];

    always @(posedge clk_125) begin
        // advance pipelines
        sr0 <= sr0_next;
        sr1 <= sr1_next;

        // register outputs (buffered)
        ld4_b_n <= ld4_b_n_next;   // exactly 3-cycle lag from sw[0]
        ld5_b_n <= ld5_b_n_next;   // exactly 3-cycle lag from sw[1]

        // keep red/green OFF (active-high -> drive low)
        ld4_r_n <= 1'b0;
        ld4_g_n <= 1'b0;
        ld5_r_n <= 1'b0;
        ld5_g_n <= 1'b0;
    end

endmodule