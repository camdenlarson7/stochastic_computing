module add8_gate(
    input  [7:0] A,
    input  [7:0] B,
    output [7:0] S,
    output       COUT
);
    wire [7:0] c; // internal carries

    // LSB: carry-in = 1'b0 for plain A + B
    full_adder fa0 (A[0], B[0], 1'b0, S[0], c[0]);
    full_adder fa1 (A[1], B[1], c[0], S[1], c[1]);
    full_adder fa2 (A[2], B[2], c[1], S[2], c[2]);
    full_adder fa3 (A[3], B[3], c[2], S[3], c[3]);
    full_adder fa4 (A[4], B[4], c[3], S[4], c[4]);
    full_adder fa5 (A[5], B[5], c[4], S[5], c[5]);
    full_adder fa6 (A[6], B[6], c[5], S[6], c[6]);
    full_adder fa7 (A[7], B[7], c[6], S[7], c[7]);

    assign COUT = c[7];
endmodule