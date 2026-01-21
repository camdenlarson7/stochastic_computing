// 1-bit full subtractor: diff = a - b - bin
// Gates only: xor, xnor (as not+xor), and, or, not
module full_subtractor (
    input  a,
    input  b,
    input  bin,       // borrow-in
    output diff,
    output bout       // borrow-out
);
    wire axb;         // a ^ b
    wire nxab;        // ~(a ^ b)

    xor  (axb,  a, b);
    xor  (diff, axb, bin);

    // bout = (~a & b) | ( (~(a ^ b)) & bin )
    wire na, t1, t2;
    not  (na, a);
    and  (t1, na, b);

    wire n_axb;
    not  (n_axb, axb);        // ~(a ^ b)
    and  (t2, n_axb, bin);
    or   (bout, t1, t2);
endmodule

