module op_lfsr (
    input [6:0] a_in, 
    input [6:0] b_in, 
    input clk, 
    input rst_n, 
    input start, 
    output reg [7:0] result, 
    output reg done
    );

    reg [7:0] lfsr_reg;
    reg [6:0] step_count;
    reg [1:0] state;

    wire feedback = lfsr_reg[7] ^ lfsr_reg[5] ^ lfsr_reg[4] ^ lfsr_reg[3];

    localparam STATE_LOAD = 2'd0;
    localparam STATE_CALC = 2'd1;
    localparam STATE_DONE = 2'd2;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            result <= 8'd0;
            done <= 1'b0;
            lfsr_reg <= 8'd0;
            step_count <= 7'd0;
            state <= STATE_LOAD;
        end
        else begin
            case (state)
                STATE_LOAD : begin
                    done <= 1'b0;
                    if (start == 1'b1) begin
                        if (a_in == 7'd0) begin
                            lfsr_reg <= 8'd1;
                        end
                        else begin
                            lfsr_reg <= {1'b0, a_in};
                        end
                        step_count <= b_in;
                        state <= STATE_CALC;
                    end
                end

                STATE_CALC : begin
                    if (step_count == 7'd0) begin
                        state <= STATE_DONE;
                    end
                    else begin
                        lfsr_reg <= {lfsr_reg[6:0], feedback};
                        step_count <= step_count - 7'd1;
                    end
                end

                STATE_DONE : begin
                    done <= 1'b1;
                    result <= lfsr_reg;
                    if (start == 1'b0) begin
                        state <= STATE_LOAD;
                    end
                end
                default: state <= STATE_LOAD;
            endcase
        end
    end
    
endmodule