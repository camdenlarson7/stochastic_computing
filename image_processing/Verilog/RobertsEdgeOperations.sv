module RobertsEdgeOperations;

reg [7:0] A, B;
reg [7:0] adds, CoutsAdd;
reg [7:0] subsAB, subsBA, CoutsSubAB, CoutsSubBA;
reg [7:0] grtrA, grtrB;
reg [7:0] absDiff;
integer i;

initial begin

A = 8'b10101001;
B = 8'b01101111;

//Addition
adds[0] = A[0] ^ B[0] ^ 1'b0;
CoutsAdd[0] = (A[0] & B[0]) | (1'b0 & (A[0] ^ B[0]));
for(int i = 1; i <= 7; i++)
begin
	adds[i] = A[i] ^ B[i] ^ CoutsAdd[i-1];
	CoutsAdd[i] = (A[i] & B[i]) | (CoutsAdd[i-1] & (A[i] ^ B[i]));
end

//Absolute Difference
//A-B
subsAB[0] = A[0] ^ B[0];
CoutsSubAB[0] = ~A[0] & B[0];
for(int i = 1; i <= 7; i++)
begin
	subsAB[i] = (A[i] ^ B[i]) ^ CoutsSubAB[i-1];
	CoutsSubAB[i] = (~A[i] & B[i]) | ((~A[i] ^ B[i]) & (CoutsSubAB[i-1]));
end

//B-A
subsBA[0] = B[0] ^ A[0];
CoutsSubBA[0] = ~B[0] & A[0];
for(int i = 1; i <= 7; i++)
begin
	subsBA[i] = (B[i] ^ A[i]) ^ CoutsSubBA[i-1];
	CoutsSubBA[i] = (~B[i] & A[i]) | ((~B[i] ^ A[i]) & (CoutsSubBA[i-1]));
end

//Comparator
grtrA[7] = A[7] & ~B[7];
grtrB[7] = ~A[7] & B[7];
for(int i = 6; i >= 0; i--)
begin
	grtrA[i] = grtrA[i+1] | ~grtrB[i+1] & (A[i] & ~B[i]);
	grtrB[i] = grtrB[i+1] | ~grtrA[i+1] & (~A[i] & B[i]);
end

//Final Difference
for(int i = 0; i <= 7; i++)
begin
	absDiff[i] = (subsAB[i] & grtrA[0]) | (subsBA[i] & ~grtrA[0]);
end


$display("inputA = %d", A);
$display("inputB = %d", B);
$display("Difference = %d", absDiff);

end

endmodule