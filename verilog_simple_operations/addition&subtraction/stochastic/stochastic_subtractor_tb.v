`timescale 1ns / 1ps

module stochastic_subtractor_tb;

    parameter BIT_LENGTH = 128;
    parameter NUM_STREAMS = 500;

    // DUT signals
    reg a, b, rand_bit;
    wire y;

    // Instantiate the subtractor (your module)
    stochastic_subtractor uut (
        .a(a),
        .b(b),
        .rand_bit(rand_bit),
        .y(y)
    );

    // Files / loop vars
    integer a_file, b_file, sel_file, y_file;
    integer i, j, rc, tmp;

    // 2-D unpacked arrays (SystemVerilog)
    reg a_vals   [0:NUM_STREAMS-1][0:BIT_LENGTH-1];
    reg b_vals   [0:NUM_STREAMS-1][0:BIT_LENGTH-1];
    reg sel_vals [0:NUM_STREAMS-1][0:BIT_LENGTH-1];
    reg y_vals   [0:NUM_STREAMS-1][0:BIT_LENGTH-1];

    initial begin
        a = 0; b = 0; rand_bit = 0;

        a_file   = $fopen("a_bits.txt",   "r");
        b_file   = $fopen("b_bits.txt",   "r");
        sel_file = $fopen("sel_bits.txt", "r");
        y_file   = $fopen("y_bits.txt",   "w");

        if (!a_file || !b_file || !sel_file || !y_file) begin
            $display("Error: Could not open one or more files");
            $finish;
        end

        // Read NUM_STREAMS × BIT_LENGTH bits
        for (i = 0; i < NUM_STREAMS; i = i + 1) begin
            for (j = 0; j < BIT_LENGTH; j = j + 1) begin
                rc = $fscanf(a_file,   "%d", tmp); a_vals[i][j]   = (tmp != 0);
                rc = $fscanf(b_file,   "%d", tmp); b_vals[i][j]   = (tmp != 0);
                rc = $fscanf(sel_file, "%d", tmp); sel_vals[i][j] = (tmp != 0);
            end
        end

        // Run subtraction stream by stream
        for (i = 0; i < NUM_STREAMS; i = i + 1) begin
            for (j = 0; j < BIT_LENGTH; j = j + 1) begin
                a        = a_vals[i][j];
                b        = b_vals[i][j];
                rand_bit = sel_vals[i][j];
                #1;
                y_vals[i][j] = y;
            end
        end

        // Write outputs
        for (i = 0; i < NUM_STREAMS; i = i + 1) begin
            for (j = 0; j < BIT_LENGTH; j = j + 1)
                $fwrite(y_file, "%0d ", y_vals[i][j]);
            $fwrite(y_file, "\n");
        end

        $display("Output written to y_bits.txt");
        $fclose(a_file); $fclose(b_file); $fclose(sel_file); $fclose(y_file);
        $finish;
    end
endmodule
