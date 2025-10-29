`timescale 1ns / 1ps
module stochastic_subtractor (
    input wire a,        // stochastic input stream 1
    input wire b,        // stochastic input stream 2
    input wire rand_bit, // random bit for multiplexing
    output wire y        // output stochastic stream
);
    // Basic idea: choose A when rand_bit=1, inverted B when rand_bit=0
    assign y = rand_bit ? a : ~b;
endmodule

