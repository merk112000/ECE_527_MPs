`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 01.09.2025 16:56:58
// Design Name: 
// Module Name: pB_rtl
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


module pB_rtl(
    input  wire        clk_125,   // 125 MHz clock
    input  wire [1:0]  sw,        // slide switches [1:0]
    input  wire [3:0]  btn,       // push buttons: btn[0]=Mode0, ... btn[3]=Mode3 (assumed active-HIGH)
    output reg  [3:0]  led        // regular LEDs LD0..LD3 (active-HIGH)
);

    // Synchronous power-on reset: stretch a reset pulse for a few cycles
    reg [3:0] por_cnt = 4'd0;
    wire      por_busy = (por_cnt != 4'hF);  // count to max, then stop
    always @(posedge clk_125) begin
        if (por_busy) por_cnt <= por_cnt + 4'd1;
    end
    wire sys_rst = por_busy; // synchronous, HIGH for first ~16 cycles


    reg [1:0] sw_s;
    wire [3:0] btn_s  = btn;   // assumed active-HIGH; invert here if board buttons are active-LOW

    // ----------------------------------------------------------------
    // FSM: mode register (2 bits: 0..3)
    // Latches on button press; persists until another button is pressed.
    // Priority: btn[3] > btn[2] > btn[1] > btn[0] (pressing multiple picks highest index)
    // Reset => Mode 0
    // ----------------------------------------------------------------

    reg[1:0] mode_n = 2'd0;
    always @(posedge clk_125) begin
        if (sys_rst) begin
            mode_n <= 2'd0; 
            sw_s <= 2'd0; end
        else begin   
            sw_s <= sw;   
                       // default: hold current state
            if      (btn_s[3]) mode_n = 2'd3;
            else if (btn_s[2]) mode_n = 2'd2;
            else if (btn_s[1]) mode_n = 2'd1;
            else if (btn_s[0]) mode_n = 2'd0;   
            
        end
    end
  

    // Base state from switches:
    // 00->0001, 01->0011, 10->0111, 11->1111
    // Formula: ((1 << (sw+1)) - 1) & 4'hF
    wire [3:0] base_state =
        (sw_s == 2'b00) ? 4'b0001 :
        (sw_s == 2'b01) ? 4'b0011 :
        (sw_s == 2'b10) ? 4'b0111 :
                          4'b1111 ;

    // Mode transforms (combinational)
    wire [3:0] mode0_out = base_state;
    wire [3:0] mode1_out = base_state >> 2;                        // logical right shift by 2
    wire [3:0] mode2_out = ((base_state << 3) | (base_state >> 1)) & 4'hF; // rotate-left by 3 (wrap)
    wire [3:0] mode3_out = ~base_state;
    
    reg [3:0] out;
    
    always @* begin
        case (mode_n)
            2'd0: out = mode0_out;
            2'd1: out = mode1_out;
            2'd2: out = mode2_out;
            default: out = mode3_out;  // safe default, avoids latches
        endcase
    end
                         
    // Registered outputs (single-cycle latency)
    always @* begin
        // no separate reset on outputs-reset effect comes from mode reset to 0     
        led = out;
    end 


endmodule