`timescale 1ns/1ps

module tb_stochastic_mult;

    // Match your generator: 2^14 = 16384
    localparam N = 16384;

    // DUT I/O
    reg  [N-1:0] a_bits, b_bits;
    wire [N-1:0] y_bits;

    stochastic_mult #(.N(N)) dut (
        .a_bits(a_bits),
        .b_bits(b_bits),
        .y_bits(y_bits)
    );

    // For file I/O
    integer fd, code;
    integer i;
    integer lineA, lineB;

    // Decimals from file
    real p_a, p_b;
    // Counts and measured probabilities
    integer ones_a, ones_b, ones_y;
    real meas_a, meas_b, meas_y;
    real expected, err;

    // Popcount helper (Verilog-2001 safe)
    function integer popcount;
        input [N-1:0] v;
        integer k, c;
        begin
            c = 0;
            for (k = 0; k < N; k = k + 1)
                c = c + (v[k] ? 1 : 0);
            popcount = c;
        end
    endfunction

    initial begin
        // === Choose which lines to read ===
        lineA = 1;  // first stochastic number
        lineB = 3;  // second stochastic number

        // Open file
        fd = $fopen("sobol_bitstreams.txt", "r");
        if (fd == 0) begin
            $display("ERROR: Could not open file");
            $finish;
        end

        // Read up to the maximum line number needed
        for (i = 1; i <= (lineA > lineB ? lineA : lineB); i = i + 1) begin
            code = $fscanf(fd, "%f,%b\n", tmp_val, tmp_bits);
            if (code != 2) begin
                $display("ERROR: Failed to read line %0d (code=%0d)", i, code);
                $finish;
            end

            if (i == lineA) begin
                p_a    = tmp_val;
                a_bits = tmp_bits;
            end
            if (i == lineB) begin
                p_b    = tmp_val;
                b_bits = tmp_bits;
            end
        end

        $fclose(fd);


        // Let combinational propagate
        #1;

        // Compute measured probabilities
        ones_a = popcount(a_bits);
        ones_b = popcount(b_bits);
        ones_y = popcount(y_bits);

        meas_a = ones_a / (1.0 * N);
        meas_b = ones_b / (1.0 * N);
        meas_y = ones_y / (1.0 * N);

        expected = p_a * p_b;
        err      = meas_y - expected;
        if (err < 0) err = -err;

        // Report
        $display("=== Stochastic Multiplication (unipolar, N=%0d) ===", N);
        $display("A: p(file)=%.3f  meas=%.6f  ones=%0d", p_a, meas_a, ones_a);
        $display("B: p(file)=%.3f  meas=%.6f  ones=%0d", p_b, meas_b, ones_b);
        $display("Y = A AND B");
        $display("Expected p_y = p_a * p_b = %.6f", expected);
        $display("Measured p_y = %.6f  ones=%0d", meas_y, ones_y);
        $display("Absolute error = %.6e", err);

        $finish;
    end

endmodule
