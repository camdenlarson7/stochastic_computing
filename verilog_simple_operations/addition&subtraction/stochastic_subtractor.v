`timescale 1ns / 1ps

// Unipolar stochastic subtractor using a random multiplexer.
// Computes approximately: (A - B + 1) / 2 to keep output in [0,1]
//
// If you use bipolar encoding ([-1, 1]), you'd implement subtraction differently.

module stochastic_subtractor (
    input wire a,        // stochastic input stream 1
    input wire b,        // stochastic input stream 2
    input wire rand_bit, // random bit for multiplexing
    output wire y        // output stochastic stream
);
    // Basic idea: choose A when rand_bit=1, inverted B when rand_bit=0
    assign y = rand_bit ? a : ~b;
endmodule

