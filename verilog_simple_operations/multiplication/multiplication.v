// Gate-level(ish) N-bit unsigned fixed-point multiplier.
// Partial products use AND gates; addition uses ripple adders
// built from half- and full-adders (no '+' operators in the datapath).
module half_adder(
    input  wire x, y,
    output wire s, c
);
    assign s = x ^ y;
    assign c = x & y;
endmodule

module full_adder(
    input  wire x, y, cin,
    output wire s, cout
);
    wire s1, c1, c2;
    assign s1  = x ^ y;
    assign s   = s1 ^ cin;
    assign c1  = x & y;
    assign c2  = s1 & cin;
    assign cout = c1 | c2;
endmodule

// Ripple-carry adder (no '+')
module ripple_adder #(
    parameter W = 32
)(
    input  wire [W-1:0] a,
    input  wire [W-1:0] b,
    input  wire         cin,
    output wire [W-1:0] sum,
    output wire         cout
);
    wire [W:0] c;
    assign c[0] = cin;
    genvar i;
    generate
        for (i = 0; i < W; i = i + 1) begin : FA_CHAIN
            full_adder fa(
                .x   (a[i]),
                .y   (b[i]),
                .cin (c[i]),
                .s   (sum[i]),
                .cout(c[i+1])
            );
        end
    endgenerate
    assign cout = c[W];
endmodule

// N-bit x N-bit -> 2N-bit array/accumulate multiplier
module mul_gate #(
    parameter N = 16  // operand width (all bits are fractional for Q0.N)
)(
    input  wire [N-1:0] a,
    input  wire [N-1:0] b,
    output wire [2*N-1:0] p
);
    // Build N partial-product rows with AND gates
    wire [N-1:0] pp [0:N-1];
    genvar r, c;
    generate
        for (r = 0; r < N; r = r + 1) begin : ROWS
            for (c = 0; c < N; c = c + 1) begin : COLS
                assign pp[r][c] = a[c] & b[r];
            end
        end
    endgenerate

    // Left-shift each row by its row index (wire placement)
    // and iteratively add them with ripple adders.
    wire [2*N-1:0] row_vec [0:N-1];
    generate
        for (r = 0; r < N; r = r + 1) begin : SHIFTED_ROWS
            // place pp[r] starting at bit r
            assign row_vec[r] = {{(2*N){1'b0}}} |
                                ({{(2*N-N){1'b0}}, pp[r]} << r);
        end
    endgenerate

    // Accumulate rows: acc[0]=0; acc[i+1]=acc[i]+row_vec[i]
    wire [2*N-1:0] acc [0:N];
    assign acc[0] = { (2*N){1'b0} };

    generate
        for (r = 0; r < N; r = r + 1) begin : ACCUM
            wire [2*N-1:0] sum_w;
            wire            cout_w;
            ripple_adder #(.W(2*N)) add_i(
                .a   (acc[r]),
                .b   (row_vec[r]),
                .cin (1'b0),
                .sum (sum_w),
                .cout(cout_w) // unused, product naturally fits 2N bits
            );
            assign acc[r+1] = sum_w;
        end
    endgenerate

    assign p = acc[N];
endmodule
