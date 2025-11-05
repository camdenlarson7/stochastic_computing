`timescale 1ns/1ps

module tb_mul_gate;

    // ==== Fixed-point format ====
    // Q0.FRAC (all bits are fractional)
    localparam FRAC = 16;
    localparam N    = FRAC; // operands are 0 <= x < 1

    // ==== DUT I/O ====
    reg  [N-1:0]   a_fp, b_fp;
    wire [2*N-1:0] p_fp;

    // Instantiate the multiplier DUT (rename here if your module is different)
    mul_gate #(.N(N)) dut (
        .a(a_fp),
        .b(b_fp),
        .p(p_fp)
    );

    // ==== Reals for checking ====
    real a_real, b_real;
    real p_real, p_expected, err;

    // Variables for truncated product view (Q0.FRAC)
    integer p_trunc;
    real    p_trunc_real;

    // ==== Fixed-point helpers (Verilog-2001 safe) ====

    // Convert real in [0,1) to Q0.FRAC integer with rounding to nearest.
    function integer to_fixed;
        input real x;
        real scaled;
        begin
            scaled = x * (1 << FRAC);
            if (scaled < 0.0) scaled = 0.0;
            if (scaled > (1 << FRAC) - 1) scaled = (1 << FRAC) - 1;
            // Verilog coerces real->int on assignment; +0.5 gives round-to-nearest.
            to_fixed = scaled + 0.5;
        end
    endfunction

    // Convert Q0.FRAC integer back to real
    function real from_fixed_a;
        input integer x;
        begin
            from_fixed_a = x / (1.0 * (1 << FRAC));
        end
    endfunction

    // Convert Q0.(2*FRAC) product back to real WITHOUT 1 << (2*FRAC)
    function real from_fixed_prod;
        input integer x;
        real scale16;   // 2^FRAC as real
        real denom;     // 2^(2*FRAC) as real, computed as (2^FRAC)*(2^FRAC)
        begin
            scale16 = 1.0 * (1 << FRAC); // 65536.0 when FRAC=16
            denom   = scale16 * scale16; // 2^(2*FRAC) as real (4,294,967,296.0)
            from_fixed_prod = x / denom;
        end
    endfunction

    // ==== Optional waveform dump ====
    initial begin
        $dumpfile("wave.vcd");
        $dumpvars(0, tb_mul_gate);
    end

    // ==== Test sequence ====
    initial begin
        // Test values
        a_real = 0.471;
        b_real = 0.652;

        // Convert to fixed-point
        a_fp = to_fixed(a_real);
        b_fp = to_fixed(b_real);

        // Let combinational logic settle
        #1;

        // Convert product back to real for comparison
        p_real     = from_fixed_prod(p_fp);
        p_expected = a_real * b_real;
        err        = p_real - p_expected;

        // Print results
        $display("=== Gate-Level Fixed-Point Multiply Test (Q0.%0d) ===", FRAC);
        $display("A (real) = %0.6f, B (real) = %0.6f", a_real, b_real);
        $display("A (fixed, 0x%0h) = %0.6f", a_fp, from_fixed_a(a_fp));
        $display("B (fixed, 0x%0h) = %0.6f", b_fp, from_fixed_a(b_fp));
        $display("P (fixed, 0x%0h)", p_fp);
        $display("P (real from fixed) = %0.9f", p_real);
        $display("Expected (double)    = %0.9f", p_expected);
        if (err < 0) err = -err;
        $display("Absolute error       = %0.9e", err);

        // Also show product truncated back to Q0.FRAC (discard low FRAC bits)
        p_trunc      = p_fp >> FRAC; // Q0.FRAC
        p_trunc_real = p_trunc / (1.0 * (1 << FRAC));
        $display("P (trunc to Q0.%0d, 0x%0h) = %0.9f", FRAC, p_trunc, p_trunc_real);

        $finish;
    end

endmodule
