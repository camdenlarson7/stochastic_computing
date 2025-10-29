
module stochastic_adder (
    input wire a,       // stochastic input stream 1
    input wire b,       // stochastic input stream 2
    input wire rand_bit, // random bit for averaging
    output wire y       // output stochastic stream
);
    assign y = rand_bit ? a : b;
endmodule
