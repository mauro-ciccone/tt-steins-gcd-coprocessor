module os_menu (
    input  wire       clk,
    input  wire       rst_n,
    input  wire [7:0] ui_in,
    input  wire       test_mode,
    output reg  [7:0] uo_out
    );
    
    reg [2:0] state;
    reg [6:0] op_code;
    reg [6:0] val_a;
    reg [6:0] val_b;
    reg [7:0] result;
    reg enter_prev;
    reg sync_0;
    reg sync_1;
    reg [19:0] debounce_cnt;
    reg debounced_enter;
    reg  timer_enable;
    reg  [1:0] display_state;
    reg start_gcd;
    reg start_isqrt;
    reg start_lfsr;

    wire enter_pulse = (debounced_enter == 1'b1) && (enter_prev == 1'b0);
    wire [7:0] decoded_result_LED;
    wire unused_dp = &{1'b0, decoded_result_LED[7]};
    wire gcd_done;
    wire [7:0] gcd_answer;
    wire [11:0] bcd_result;
    wire timer_tick;
    wire [3:0] current_digit = (display_state == 2'd0) ? bcd_result[11:8] :
                               (display_state == 2'd1) ? bcd_result[7:4]  : 
                                                         bcd_result[3:0];
    wire isqrt_done;
    wire [7:0] isqrt_answer;
    wire lfsr_done;
    wire [7:0] lfsr_answer;
    wire [19:0] debounce_limit = (test_mode == 1'b1) ? 20'd5 : 20'd1000000;
    

    localparam STATE_MENU = 3'd0;
    localparam STATE_LOAD_A = 3'd1;
    localparam STATE_LOAD_B = 3'd2;
    localparam STATE_CALC = 3'd3;
    localparam STATE_DONE = 3'd4;

    localparam MENU_LED = 8'b01101101;
    localparam LOAD_A_LED = 8'b01110111;
    localparam LOAD_B_LED = 8'b01111111;
    localparam CALC_LED = 8'b01000000;

    bin_to_bcd math_translator (
        .bin (result),
        .bcd (bcd_result)
    );

    delay_timer ui_timer (
        .clk    (clk),
        .rst_n  (rst_n),
        .enable (timer_enable),
        .test_mode (test_mode),
        .tick   (timer_tick)
    );

    led_decoder final_display (
        .a (current_digit),
        .y (decoded_result_LED)
    );

    op_gcd gcd_coprocessor (
        .a_in   (val_a),
        .b_in   (val_b),
        .clk    (clk),
        .rst_n  (rst_n),
        .start  (start_gcd),
        .result   (gcd_answer),
        .done (gcd_done)
    );

    op_isqrt sqrt_coprocessor (
    .a_in   (val_a),
    .b_in   (val_b),
    .clk    (clk),
    .rst_n  (rst_n),
    .start  (start_isqrt),
    .result (isqrt_answer),
    .done   (isqrt_done)
    );

    op_lfsr prng_coprocessor (
        .a_in   (val_a),
        .b_in   (val_b),
        .clk    (clk),
        .rst_n  (rst_n),
        .start  (start_lfsr),
        .result (lfsr_answer),
        .done   (lfsr_done)
    );

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= 3'b000;
            op_code <= 7'd0;
            val_a <= 7'd0;
            val_b <= 7'd0;
            result <= 8'd0;
            enter_prev <= 1'b0;
            sync_0 <= 1'b0;
            sync_1 <= 1'b0;
            debounce_cnt <= 20'd0;
            debounced_enter <= 1'b0;
            uo_out <= 8'd0;
            start_gcd <= 1'b0;
            timer_enable <= 1'b0;
            display_state <= 2'd0;
            start_isqrt <= 1'b0;
            start_lfsr <= 1'b0;
        end
        else begin

            sync_0 <= ui_in[7];
            sync_1 <= sync_0;

            if (debounced_enter == sync_1) begin
                debounce_cnt <= 20'd0;
            end
            else begin
                debounce_cnt <= debounce_cnt + 1'b1;
                if (debounce_cnt >= debounce_limit) begin
                    debounced_enter <= sync_1;
                    debounce_cnt <= 20'd0;
                end
            end


            enter_prev <= debounced_enter;

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

                    case (op_code)
                        7'd0 : begin
                            if (gcd_done == 1'b1) begin
                                result <= gcd_answer;
                                start_gcd <= 1'b0;
                                state <= STATE_DONE;
                            end
                            else begin
                                start_gcd <= 1'b1;
                            end
                        end
                        7'd1 : begin
                            if (isqrt_done == 1'b1) begin
                                result <= isqrt_answer;
                                start_isqrt <= 1'b0;
                                state <= STATE_DONE;
                            end
                            else begin
                                start_isqrt <= 1'b1;
                            end
                        end
                        7'd2 : begin
                            if (lfsr_done == 1'b1) begin
                                result <= lfsr_answer;
                                start_lfsr <= 1'b0;
                                state <= STATE_DONE;
                            end
                            else begin
                                start_lfsr <= 1'b1;
                            end
                        end
                        //add here the other operations
                        default: begin
                            state <= STATE_MENU;
                        end
                    endcase
                end
                STATE_DONE : begin
                    if (display_state == 2'd0) begin
                        uo_out <= {1'b1, decoded_result_LED[6:0]};
                    end else begin
                        uo_out <= {1'b0, decoded_result_LED[6:0]}; 
                    end
                    timer_enable <= 1'b1;

                    if (enter_pulse == 1) begin
                        timer_enable <= 1'b0;
                        display_state <= 2'd0;
                        state <= STATE_MENU;
                    end
                    else if (timer_tick == 1'b1) begin
                        if (display_state == 2'd2) begin
                            display_state <= 2'd0;
                        end
                        else begin
                            display_state <= display_state + 1'b1;
                        end
                    end
                end
                default: state <= 3'd0;
            endcase
        end
    end

endmodule