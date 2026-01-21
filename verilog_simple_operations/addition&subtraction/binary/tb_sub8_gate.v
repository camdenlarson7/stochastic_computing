`timescale 1ns/1ps
module tb_sub8_gate;
    reg  [7:0] A, B;
    wire [7:0] D;
    wire       BOUT;

    integer i;
    integer errors;

    // DUT
    sub8_gate dut (.A(A), .B(B), .D(D), .BOUT(BOUT));

    // Simple check task
    task check(input [7:0] a, input [7:0] b);
        reg [7:0] expD;
        reg       expBout;
    begin
        A = a; B = b;
        #1; // small delay for gate settle

        // Unsigned subtract: borrow occurs if a < b
        expD    = a - b;
        expBout = (a < b);

        if (D !== expD || BOUT !== expBout) begin
            $display("FAIL: A=%0d (0x%02h)  B=%0d (0x%02h)  -> D=%0d/0x%02h  BOUT=%b  (exp D=%0d/0x%02h, BOUT=%b)",
                      a, a, b, b, D, D, BOUT, expD, expD, expBout);
            errors = errors + 1;
        end else begin
            $display("PASS: A=%0d (0x%02h)  B=%0d (0x%02h)  -> D=%0d/0x%02h  BOUT=%b",
                      a, a, b, b, D, D, BOUT);
        end
    end
    endtask

    initial begin
        errors = 0;

        // Directed tests (edge cases)
        check(8'h00, 8'h00); // 0 - 0
        check(8'h00, 8'h01); // 0 - 1 -> borrow
        check(8'h01, 8'h00); // 1 - 0
        check(8'hFF, 8'h01); // 255 - 1
        check(8'h80, 8'h80); // 128 - 128
        check(8'h7F, 8'h80); // 127 - 128 -> borrow
        check(8'h10, 8'h10); // equal
        check(8'h10, 8'h1F); // borrow
        check(8'hA5, 8'h5A); // mixed pattern
        check(8'h5A, 8'hA5); // inverse -> borrow

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
