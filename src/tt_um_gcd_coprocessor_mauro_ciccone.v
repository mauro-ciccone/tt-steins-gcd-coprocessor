/*
 * Copyright (c) 2024 Mauro Ciccone
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_gcd_coprocessor_mauro_ciccone (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  assign uio_out = 8'b0;
  assign uio_oe  = 8'b0;

  os_menu my_control_unit (
      .clk    (clk),
      .rst_n  (rst_n),
      .ui_in  (ui_in),   // Passing the 8 switches into the OS
      .uo_out (uo_out)   // Letting the OS control the 7-segment display
  );

  // List all unused inputs to prevent warnings
  wire _unused = &{ena, uio_in[7:0], 1'b0};

endmodule