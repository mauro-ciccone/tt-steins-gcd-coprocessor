module euclideanSteinFSM (
    input [6:0] a_in, 
    input [6:0] b_in, 
    input clk, 
    input rst_n, 
    input start, 
    output reg [7:0] result, 
    output reg done
    );

    reg [6:0] a_reg, b_reg, divisions;
    reg [1:0] state;

    parameter STATE_LOAD = 2'b00;
    parameter STATE_CALC = 2'b01;
    parameter STATE_DONE = 2'b10;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= STATE_LOAD;
            a_reg <= 7'd0;
            b_reg <= 7'd0;
            result <= 8'd0;
            done <= 1'b0;
            divisions <= 7'd0;
        end
        else begin
            case (state)
                STATE_LOAD : begin
                    a_reg <= a_in;
                    b_reg <= b_in;
                    done <= 1'b0;
                    divisions <= 7'd0;
                    if (start) begin
                        state <= STATE_CALC;
                    end
                end

                STATE_CALC : begin
                    done <= 1'b0;
                    if (b_reg == 0 || a_reg == b_reg) begin
                        state <= STATE_DONE;
                    end
                    else if (a_reg == 0) begin
                        a_reg <= b_reg;
                        state <= STATE_DONE;
                    end
                    else if (a_reg[0] == 0 && b_reg[0] == 0) begin
                        a_reg <= a_reg >> 1;
                        b_reg <= b_reg >> 1;
                        divisions <= divisions + 1;
                    end
                    else if (a_reg[0] == 0 && b_reg[0] == 1) begin
                        a_reg <= a_reg >> 1;
                    end
                    else if (a_reg[0] == 1 && b_reg[0] == 0) begin
                        b_reg <= b_reg >> 1;
                    end
                    else begin
                        if (a_reg > b_reg) begin
                            a_reg <= (a_reg - b_reg) >> 1;
                        end
                        else begin
                            b_reg <= (b_reg - a_reg) >> 1;
                        end
                    end
                end

                STATE_DONE : begin
                    result <= {1'b0, a_reg} << divisions;
                    done <= 1'b1;
                    if (!start) begin
                        state <= STATE_LOAD;
                    end
                end

                default: state <= STATE_LOAD;
            endcase
        end
        
    end
    
endmodule