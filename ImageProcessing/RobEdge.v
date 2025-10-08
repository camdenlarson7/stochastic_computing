module RobEdge(G, P1, P2, P3, P4);
output G;
input P1, P2, P3, P4;

assign G = (P1 - P4) + (P2 - P3); //in progress

endmodule
