// 8-bit ripple subtractor using 1-bit full subtractors
// Computes D = A - B, with final borrow-out BOUT.
module sub8_gate (
    input  [7:0] A,
    input  [7:0] B,
    output [7:0] D,
    output       BOUT
);
    wire [7:0] b; // internal borrows

    // LSB: borrow-in = 1'b0 for plain A - B
    full_subtractor fs0 (A[0], B[0], 1'b0, D[0], b[0]);
    full_subtractor fs1 (A[1], B[1], b[0], D[1], b[1]);
    full_subtractor fs2 (A[2], B[2], b[1], D[2], b[2]);
    full_subtractor fs3 (A[3], B[3], b[2], D[3], b[3]);
    full_subtractor fs4 (A[4], B[4], b[3], D[4], b[4]);
    full_subtractor fs5 (A[5], B[5], b[4], D[5], b[5]);
    full_subtractor fs6 (A[6], B[6], b[5], D[6], b[6]);
    full_subtractor fs7 (A[7], B[7], b[6], D[7], b[7]);

    assign BOUT = b[7];
endmodule
