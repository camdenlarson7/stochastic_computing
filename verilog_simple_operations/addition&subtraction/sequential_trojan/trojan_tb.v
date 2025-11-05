`timescale 1ns / 1ps

module stochastic_adder_trojan_tb;

    parameter BIT_LENGTH  = 128;
    parameter NUM_STREAMS = 500;

    // --- I/O staging / housekeeping
    integer rc, tmp;
    integer a_file, b_file, sel_file;
    integer y_clean_file, y_trojan_file, y_file_mirror; // mirror = y_bits.txt

    integer i, j;

    // --- DUT signals
    reg  a, b, rand_bit;

    // clock/reset for sequential trojan
    reg  clk;
    reg  rst_n;

    // trojan controls
    reg  trigger;      // external trigger (s0)
    reg  T_payload;    // Trojan value (T)

    wire y_clean;      // output of adder (no trojan)
    wire y_trojan;     // output after trojan mux

    // optional observability
    wire trojan_active;
    wire trojan_hit;
    wire [31:0] trojan_count;

    // --- Memories (2-D unpacked arrays)
    reg a_vals        [0:NUM_STREAMS-1][0:BIT_LENGTH-1];
    reg b_vals        [0:NUM_STREAMS-1][0:BIT_LENGTH-1];
    reg sel_vals      [0:NUM_STREAMS-1][0:BIT_LENGTH-1];
    reg y_clean_vals  [0:NUM_STREAMS-1][0:BIT_LENGTH-1];
    reg y_trojan_vals [0:NUM_STREAMS-1][0:BIT_LENGTH-1];

    // =========================================
    //  DUTs
    // =========================================
    stochastic_adder uut_adder (
        .a(a),
        .b(b),
        .rand_bit(rand_bit),
        .y(y_clean)
    );

    // Default trojan: arms at cycle 64 for 64 cycles, hits every cycle,
    // payload mode 0 = invert bit_in (you can change params below).
    seq_trojan #(
        .COUNTER_WIDTH (32),
        .START_CYCLE   (64),
        .ACTIVE_CYCLES (64),
        .HIT_EVERY     (1),
        .PAYLOAD_MODE  (0)   // 0: invert; 1: force1; 2: force0; 3: bit_in^T; 4: T
    ) uut_trojan (
        .clk      (clk),
        .rst_n    (rst_n),
        .bit_in   (y_clean),
        .trigger  (trigger),
        .T        (T_payload),
        .bit_out  (y_trojan),
        .active   (trojan_active),
        .hit_pulse(trojan_hit),
        .count    (trojan_count)
    );

    // =========================================
    //  Clock / Reset
    // =========================================
    initial begin
        clk = 1'b0;
        forever #0.5 clk = ~clk;  // 1.0 time-unit period; one bit per posedge
    end

    initial begin
        rst_n = 1'b0;
        #1;           // hold reset for one clock
        rst_n = 1'b1;
    end

    // =========================================
    //  Main TB
    // =========================================
    initial begin
        a = 0; b = 0; rand_bit = 0;
        trigger = 1'b1;          // keep trigger asserted; trojan window & divider gate it
        T_payload = 1'b1;        // payload value used by modes 3/4; ignored by others

        $display("Reading multi-row bitstreams...");

        a_file         = $fopen("a_bits.txt",   "r");
        b_file         = $fopen("b_bits.txt",   "r");
        sel_file       = $fopen("sel_bits.txt", "r");
        y_clean_file   = $fopen("y_clean_bits.txt",   "w");
        y_trojan_file  = $fopen("y_trojan_bits.txt",  "w");
        y_file_mirror  = $fopen("y_bits.txt",         "w"); // mirror for your existing Python

        if (!a_file || !b_file || !sel_file ||
            !y_clean_file || !y_trojan_file || !y_file_mirror) begin
            $display("Error: Could not open one or more files.");
            $finish;
        end

        // --- Read inputs into arrays
        for (i = 0; i < NUM_STREAMS; i = i + 1) begin
            for (j = 0; j < BIT_LENGTH; j = j + 1) begin
                rc = $fscanf(a_file,   "%d", tmp); a_vals[i][j]   = (tmp != 0);
                rc = $fscanf(b_file,   "%d", tmp); b_vals[i][j]   = (tmp != 0);
                rc = $fscanf(sel_file, "%d", tmp); sel_vals[i][j] = (tmp != 0);
            end
        end

        // --- Drive streams bit-by-bit synchronized to clock
        // Set inputs on negedge, sample outputs on following posedge.
        for (i = 0; i < NUM_STREAMS; i = i + 1) begin
            $display("---- Stream %0d ----", i);
            for (j = 0; j < BIT_LENGTH; j = j + 1) begin
                @(negedge clk);
                a        = a_vals[i][j];
                b        = b_vals[i][j];
                rand_bit = sel_vals[i][j];

                @(posedge clk);   // trojan counter ticks + outputs settle
                y_clean_vals[i][j]  = y_clean;
                y_trojan_vals[i][j] = y_trojan;

                $display("t%0d | bit %0d: a=%0d b=%0d sel=%0d | y=%0d  yT=%0d | active=%0d hit=%0d",
                         trojan_count, j, a, b, rand_bit, y_clean, y_trojan, trojan_active, trojan_hit);
            end
        end

        // --- Write results
        for (i = 0; i < NUM_STREAMS; i = i + 1) begin
            for (j = 0; j < BIT_LENGTH; j = j + 1) begin
                $fwrite(y_clean_file,  "%0d ", y_clean_vals[i][j]);
                $fwrite(y_trojan_file, "%0d ", y_trojan_vals[i][j]);
                $fwrite(y_file_mirror, "%0d ", y_trojan_vals[i][j]); // mirror as y_bits.txt
            end
            $fwrite(y_clean_file,  "\n");
            $fwrite(y_trojan_file, "\n");
            $fwrite(y_file_mirror, "\n");
        end

        $display("Done! Outputs: y_clean_bits.txt, y_trojan_bits.txt (and y_bits.txt mirror).");
        $fclose(a_file);
        $fclose(b_file);
        $fclose(sel_file);
        $fclose(y_clean_file);
        $fclose(y_trojan_file);
        $fclose(y_file_mirror);
        $finish;
    end
endmodule
