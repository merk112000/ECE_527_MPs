`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 01.09.2025 18:16:07
// Design Name: 
// Module Name: pB_testbench
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


module pB_testbench;
    reg        clk;
    reg  [1:0] sw;
    reg  [3:0] btn;
    wire [3:0] led;

    // DUT
    pB_rtl dut (
        .clk_125(clk),
        .sw(sw),
        .btn(btn),
        .led(led)
    );

    // 125 MHz clock (8 ns period)
    initial clk = 1'b0;
    always #4 clk = ~clk;

    
    function [3:0] base_state(input [1:0] s);
        case (s)
            2'b00: base_state = 4'b0001;
            2'b01: base_state = 4'b0011;
            2'b10: base_state = 4'b0111;
            default: base_state = 4'b1111;
        endcase
    endfunction

    function [3:0] xform(input [3:0] b, input [1:0] m);
        case (m)
            2'd0: xform = b;                                         // Mode 0
            2'd1: xform = b >> 2;                                   // Mode 1: logical right 2
            2'd2: xform = ((b << 3) | (b >> 1)) & 4'hF;             // Mode 2: rotl3 on 4 bits
            default: xform = ~b & 4'hF;                             // Mode 3: invert
        endcase
    endfunction

    // Track expected mode (latched on a button press; priority 3..0)
    reg [1:0] mode_ref;
    integer i;

    // Utility: check LED matches golden after 1-cycle latency
    task check_led(input [1:0] sw_val, input [1:0] mode_val, input [255:0] tag);
        reg [3:0] exp;
    begin
        exp = xform(base_state(sw_val), mode_val);
       @(posedge clk);
        if (led !== exp) begin
            $display("[%0t] MISMATCH %s  sw=%b mode=%0d  led=%b exp=%b",
                     $time, tag, sw_val, mode_val, led, exp);
        end
    end
    endtask

    // Utility: pulse exactly one button (one-hot), update mode_ref accordingly, check next cycle
    task press_one_button(input [3:0] onehot_btn, inout [1:0] mode_ref_io, input [1:0] sw_hold, input [255:0] tag);
        reg [1:0] new_mode;
    begin
        // derive target mode from which button is high
        case (onehot_btn)
            4'b0001: new_mode = 2'd0;
            4'b0010: new_mode = 2'd1;
            4'b0100: new_mode = 2'd2;
            4'b1000: new_mode = 2'd3;
            default: new_mode = mode_ref_io; // should be one-hot
        endcase
        #2;
        sw  = sw_hold;
        btn = onehot_btn;
        @(posedge clk); 
        #1;           // sampled here
        btn = 4'b0000;             // release immediately (don't need to hold)
        mode_ref_io = new_mode;    // TB mirrors DUT's latched mode

        // verify one-cycle latency to LED output
        check_led(sw_hold, mode_ref_io, tag);
    end
    endtask

    initial begin
        sw       = 2'b00;
        btn      = 4'b0000;
        mode_ref = 2'd0;

        // Allow DUT's synchronous POR (if present) to settle
        repeat (20) @(posedge clk);
        #1;
        btn      = 4'b0001;
        // ================== 1) Baseline: Mode 0, sweep switches ==================
        for (i = 0; i < 4; i = i + 1) begin
            #1;
            sw = i[1:0];
            @(posedge clk);
            #1;
            btn = 0; 
            check_led(sw, mode_ref, "Baseline M0 sweep");
             #2;
        end
        #1;
        btn = 4'b0000;
        @(posedge clk); 
         #1;
        // ================== 2) Set Mode 1, sweep switches ==================
        btn = 4'b0010; 
        
        mode_ref = 2'd1;
        
        for (i = 0; i < 4; i = i + 1) begin
            #1;
            sw = i[1:0];
            @(posedge clk);
            #1;
            btn = 0;
            check_led(sw, mode_ref, "M1 sweep");
            
            #2;
        end
        #1;
        btn = 4'b0000;
        @(posedge clk);
        
        #1;
        // ================== 3) Set Mode 2, sweep switches ==================
        btn = 4'b0100; 
        
        mode_ref = 2'd2;
        for (i = 0; i < 4; i = i + 1) begin
            #1;
            sw = i[1:0];
            @(posedge clk);
            #1;
            btn = 4'b0000;
            check_led(sw, mode_ref, "M2 sweep");
           
            #2;
        end

        @(posedge clk);
        #1;
        // ================== 4) Set Mode 3, sweep switches ==================
        btn = 4'b1000; 

        mode_ref = 2'd3;
        for (i = 0; i < 4; i = i + 1) begin
            #1;
            sw = i[1:0];
            @(posedge clk);
             #1;
             btn = 4'b0000;
            check_led(sw, mode_ref, "M3 sweep");
            #2;
        end
        
       #1;
        btn = 4'b0000; 
        @(posedge clk);
        #2;

        // ================== 5) Priority: multiple buttons at once ==================
        sw = 2'b10; btn = 4'b1101; // 3,2,0 pressed → 3 must win
        @(posedge clk); 
        #1;
        btn = 4'b0000;
        mode_ref = 2'd3;
        check_led(sw, mode_ref, "Multi-button priority (3 wins)");
        @(posedge clk);
            #2;

        // ================== 6)  Steady SW, walk through modes 0→1→2→3 ==================
        sw = 2'b01;
        // Force Mode 0, then step modes with only buttons changing
        press_one_button(4'b0001, mode_ref, sw, "Steady SW: set M0");
        press_one_button(4'b0010, mode_ref, sw, "Steady SW: M0→M1");
        press_one_button(4'b0100, mode_ref, sw, "Steady SW: M1→M2");
        press_one_button(4'b1000, mode_ref, sw, "Steady SW: M2→M3");

        // ================== 7) NEW: Back-to-back different buttons on consecutive cycles ==================
        #2;
        sw = 2'b10;
        press_one_button(4'b0001, mode_ref, sw, "Back-to-back: →M0");
        press_one_button(4'b0010, mode_ref, sw, "Back-to-back: M0→M1");
        press_one_button(4'b0100, mode_ref, sw, "Back-to-back: M1→M2");
        press_one_button(4'b0010, mode_ref, sw, "Back-to-back: M2→M1");

        // ================== 8) NEW: Hold a button high multiple cycles (should latch once, no glitches) ==================
        #2;
        sw  = 2'b11;
        btn = 4'b0100; // request M2 and HOLD
        @(posedge clk); mode_ref = 2'd2;  // sampled here
        // First check after one cycle:
        check_led(sw, mode_ref, "Hold btn: first check");
        // Keep holding for a few more cycles; LED must remain stable
        repeat (3) begin
            @(posedge clk); #1;
            if (led !== xform(base_state(sw), mode_ref)) begin
                $display("[%0t] MISMATCH Hold btn: steady led=%b exp=%b",
                         $time, led, xform(base_state(sw), mode_ref));
            end
        end
        btn = 4'b0000; // release


        $display("TB done.");
        $finish;
    end
endmodule