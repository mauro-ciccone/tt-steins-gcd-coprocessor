module os_menu (
    input  wire       clk,
    input  wire       rst_n,
    input  wire [7:0] ui_in,
    output reg  [7:0] uo_out
);
    
    reg [2:0] state;
    reg [6:0] op_code;
    reg [6:0] val_a;
    reg [6:0] val_b;
    reg [7:0] result;
    reg enter_prev;

    wire enter_pulse = (ui_in[7] == 1'b1) && (enter_prev == 1'b0);
    wire [7:0] decoded_result_LED;

    localparam STATE_MENU = 3'd0;
    localparam STATE_LOAD_A = 3'd1;
    localparam STATE_LOAD_B = 3'd2;
    localparam STATE_CALC = 3'd3;
    localparam STATE_DONE = 3'd4;

    localparam MENU_LED = 8'b01101101;
    localparam LOAD_A_LED = 8'b01110111;
    localparam LOAD_B_LED = 8'b01111111;
    localparam CALC_LED = 8'b01000000;

    decoderLED temporary_display (
        .a (result[3:0]),
        .y (decoded_result_LED)
    );

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= 3'b000;
            op_code <= 7'd0;
            val_a <= 7'd0;
            val_b <= 7'd0;
            result <= 8'd0;
            enter_prev <= 1'b0;
            uo_out <= 8'd0;
        end
        else begin
            enter_prev <= ui_in[7];

            case (state)
                STATE_MENU : begin
                    uo_out <= MENU_LED;
                    if (enter_pulse == 1) begin
                        op_code <= ui_in[6:0];
                        state <= STATE_LOAD_A;
                    end
                end
                STATE_LOAD_A : begin
                    uo_out <= LOAD_A_LED;
                    if (enter_pulse == 1) begin
                        val_a <= ui_in[6:0];
                        state <= STATE_LOAD_B;
                    end
                end
                STATE_LOAD_B : begin
                    uo_out <= LOAD_B_LED;
                    if (enter_pulse == 1) begin
                        val_b <= ui_in[6:0];
                        state <= STATE_CALC;
                    end
                end
                STATE_CALC : begin
                    uo_out <= CALC_LED; //currently invisible but maybe later visible when waiting for op
                    result <= (val_a + val_b);  //temporary test op, later here will be the result of the active operation
                    state <= STATE_DONE;
                end
                STATE_DONE : begin
                    uo_out <= decoded_result_LED;
                    if (enter_pulse == 1) begin
                        state <= STATE_MENU;
                    end
                end
                default: state <= 3'd0;
            endcase
        end
    end
endmodule