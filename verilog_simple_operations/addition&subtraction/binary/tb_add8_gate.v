`timescale 1ns/1ps
module tb_add8_gate;
    reg  [7:0] A, B;
    wire [7:0] S;
    wire       COUT;

    integer i;
    integer errors;

    // DUT
    add8_gate dut (.A(A), .B(B), .S(S), .COUT(COUT));

    // Simple check task
    task check(input [7:0] a, input [7:0] b);
        reg [7:0] expS;
        reg       expCout;
    begin
        A = a; B = b;
        #1; // small delay for gate settle

        // Unsigned addition
        {expCout, expS} = a + b;

        if (S !== expS || COUT !== expCout) begin
            $display("FAIL: A=%0d (0x%02h)  B=%0d (0x%02h)  -> S=%0d/0x%02h  COUT=%b  (exp S=%0d/0x%02h, COUT=%b)",
                      a, a, b, b, S, S, COUT, expS, expS, expCout);
            errors = errors + 1;
        end else begin
            $display("PASS: A=%0d (0x%02h)  B=%0d (0x%02h)  -> S=%0d/0x%02h  COUT=%b",
                      a, a, b, b, S, S, COUT);
        end
    end
    endtask

    initial begin
        errors = 0;

        // Directed tests (edge cases)
        check(8'h00, 8'h00); // 0 + 0
        check(8'h00, 8'h01); // 0 + 1
        check(8'h01, 8'h00); // 1 + 0
        check(8'hFF, 8'h01); // 255 + 1 -> carry
        check(8'h80, 8'h80); // 128 + 128 -> carry
        check(8'h7F, 8'h80); // 127 + 128 -> carry
        check(8'h10, 8'h10); // simple

        // Some random tests
        for (i = 0; i < 20; i = i + 1) begin
            check($random, $random);
        end

        if (errors == 0)
            $display("\nAll tests PASSED.");
        else
            $display("\nTOTAL FAILURES: %0d", errors);

        $finish;
    end
endmodule