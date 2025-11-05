`timescale 1ns / 1ps

module stochastic_subtractor_tb;

    parameter BIT_LENGTH = 128;
    parameter NUM_STREAMS = 500;


    reg a, b, rand_bit;
    wire y;

    // Instantiate the stochastic subtractor
    stochastic_subtractor uut (
        .a(a),
        .b(b),
        .rand_bit(rand_bit),
        .y(y)
    );

    // File handles
    integer a_file, b_file, sel_file, y_file;
    integer i, j;


    reg a_vals   [0:NUM_STREAMS-1][0:BIT_LENGTH-1];
    reg b_vals   [0:NUM_STREAMS-1][0:BIT_LENGTH-1];
    reg sel_vals [0:NUM_STREAMS-1][0:BIT_LENGTH-1];
    reg y_vals   [0:NUM_STREAMS-1][0:BIT_LENGTH-1];

    initial begin

        a_file  = $fopen("a_bits.txt", "r");
        b_file  = $fopen("b_bits.txt", "r");
        sel_file = $fopen("sel_bits.txt", "r");
        y_file  = $fopen("y_bits.txt", "w");

        if (!a_file || !b_file || !sel_file) begin
            $display("Error: Could not open input files");
            $finish;
        end

        // Read matrix row by row (NUM_STREAMS × BIT_LENGTH)
        for (i = 0; i < NUM_STREAMS; i = i + 1) begin
            for (j = 0; j < BIT_LENGTH; j = j + 1) begin
                $fscanf(a_file, "%d", a_vals[i][j]);
                $fscanf(b_file, "%d", b_vals[i][j]);
                $fscanf(sel_file, "%d", sel_vals[i][j]);
            end
        end


        // Perform subtraction stream by stream
        for (i = 0; i < NUM_STREAMS; i = i + 1) begin
            $display("---- Stream %0d ----", i);
            for (j = 0; j < BIT_LENGTH; j = j + 1) begin
                a = a_vals[i][j];
                b = b_vals[i][j];
                rand_bit = sel_vals[i][j];
                #1; // small delay per bit
                y_vals[i][j] = y;
                $display("Stream %0d Bit %0d: a=%0d b=%0d sel=%0d -> y=%0d",
                         i, j, a, b, rand_bit, y);
            end
        end

        // Write y bits to file row by row
        for (i = 0; i < NUM_STREAMS; i = i + 1) begin
            for (j = 0; j < BIT_LENGTH; j = j + 1)
                $fwrite(y_file, "%0d ", y_vals[i][j]);
            $fwrite(y_file, "\n");
        end

        $display("Output written to y_bits.txt");
        $fclose(a_file);
        $fclose(b_file);
        $fclose(sel_file);
        $fclose(y_file);
        $finish;
    end
endmodule
