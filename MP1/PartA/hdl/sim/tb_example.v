`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 01.09.2025 15:49:14
// Design Name: 
// Module Name: pA_testbench
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


module pA_testbench;
    reg        clk;
    reg  [1:0] sw;
    wire       ld4_b_n, ld4_r_n, ld4_g_n, ld5_b_n, ld5_r_n, ld5_g_n;

    // DUT
    pA_rtl dut (
        .clk_125(clk),
        .sw(sw),
        .ld4_b_n(ld4_b_n), .ld4_r_n(ld4_r_n), .ld4_g_n(ld4_g_n),
        .ld5_b_n(ld5_b_n), .ld5_r_n(ld5_r_n), .ld5_g_n(ld5_g_n)
    );

    // 125 MHz clock: T = 8 ns
    initial clk = 1'b0;
    always #4 clk = ~clk;

    // Reference 3-cycle delay model for checking
    reg [2:0] sr0_ref = 3'b000;
    reg [2:0] sr1_ref = 3'b000;

    task step_and_check;
        input [1:0] new_sw;
        integer i;
    begin
        sw = new_sw;
        // advance one cycle and update reference shift regs
        @(posedge clk);
        sr0_ref <= {sr0_ref[1:0], sw[0]};
        sr1_ref <= {sr1_ref[1:0], sw[1]};
        // do two more cycles to complete 3-cycle lag
        repeat (2) begin
            @(posedge clk);
            sr0_ref <= {sr0_ref[1:0], sw[0]};
            sr1_ref <= {sr1_ref[1:0], sw[1]};
        end

        // After 3 posedges, outputs should match inverted ref bit
        #1;
        if (ld4_b_n !== ~sr0_ref[2]) $display("Mismatch LD4_B_N exp=%0b got=%0b (sw=%b)", ~sr0_ref[2], ld4_b_n, sw);
        if (ld5_b_n !== ~sr1_ref[2]) $display("Mismatch LD5_B_N exp=%0b got=%0b (sw=%b)", ~sr1_ref[2], ld5_b_n, sw);
        if (ld4_r_n !== 1'b1 || ld4_g_n !== 1'b1 || ld5_r_n !== 1'b1 || ld5_g_n !== 1'b1)
            $display("R/G should be OFF (high).");
    end
    endtask

    initial begin
        sw = 2'b00;
        // let things settle
        repeat (5) @(posedge clk);

        // Exhaustive toggles with 3-cycle check after each change
        step_and_check(2'b00);
        step_and_check(2'b01);
        step_and_check(2'b10);
        step_and_check(2'b11);

        // Also test rapid flipping
        step_and_check(2'b01);
        step_and_check(2'b00);
        step_and_check(2'b11);
        step_and_check(2'b10);

        $display("TB finished.");
        $finish;
    end
endmodule