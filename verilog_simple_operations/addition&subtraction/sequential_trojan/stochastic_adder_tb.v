`timescale 1ns / 1ps

module stochastic_adder_tb;

    parameter BIT_LENGTH  = 128;
    parameter NUM_STREAMS = 500;

    integer rc, tmp; // tmp: staging var for $fscanf

    // DUT signals
    reg a, b, rand_bit;
    wire y;

    stochastic_adder uut (
        .a(a),
        .b(b),
        .rand_bit(rand_bit),
        .y(y)
    );

    // File handles
    integer a_file, b_file, sel_file, y_file;
    integer i, j;

    // 2-D unpacked arrays
    reg a_vals   [0:NUM_STREAMS-1][0:BIT_LENGTH-1];
    reg b_vals   [0:NUM_STREAMS-1][0:BIT_LENGTH-1];
    reg sel_vals [0:NUM_STREAMS-1][0:BIT_LENGTH-1];
    reg y_vals   [0:NUM_STREAMS-1][0:BIT_LENGTH-1];

    initial begin
        a = 0; b = 0; rand_bit = 0;

        $display("Reading multi-row bitstreams...");

        a_file   = $fopen("a_bits.txt",   "r");
        b_file   = $fopen("b_bits.txt",   "r");
        sel_file = $fopen("sel_bits.txt", "r");
        y_file   = $fopen("y_bits.txt",   "w");

        if (!a_file || !b_file || !sel_file || !y_file) begin
            $display("Error: Could not open one or more files.");
            $finish;
        end

        // Read all input streams (stage into tmp, then assign)
        for (i = 0; i < NUM_STREAMS; i = i + 1) begin
            for (j = 0; j < BIT_LENGTH; j = j + 1) begin
                rc = $fscanf(a_file,   "%d", tmp); a_vals[i][j]   = (tmp != 0);
                rc = $fscanf(b_file,   "%d", tmp); b_vals[i][j]   = (tmp != 0);
                rc = $fscanf(sel_file, "%d", tmp); sel_vals[i][j] = (tmp != 0);
                // if (rc != 1) $display("Warning: fscanf short read at stream %0d bit %0d", i, j);
            end
        end

        // Perform addition stream by stream
        for (i = 0; i < NUM_STREAMS; i = i + 1) begin
            $display("---- Stream %0d ----", i);
            for (j = 0; j < BIT_LENGTH; j = j + 1) begin
                a        = a_vals[i][j];
                b        = b_vals[i][j];
                rand_bit = sel_vals[i][j];
                #1;
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

        $display("Done! Output written to y_bits.txt");
        $fclose(a_file);
        $fclose(b_file);
        $fclose(sel_file);
        $fclose(y_file);
        $finish;
    end
endmodule
