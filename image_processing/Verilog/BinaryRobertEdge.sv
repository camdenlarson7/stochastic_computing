module BinaryRobertEdge;

initial
begin

integer txtfile, outputfile;
integer i, j, k;
reg [7:0] image[0:293][0:439], edges[0:292][0:438];
reg [7:0] subsAB, subsBA, CoutsSubAB, CoutsSubBA, grtrA, grtrB, absDiff;
reg [7:0] subsABx, subsBAx, CoutsSubABx, CoutsSubBAx, grtrAx, grtrBx, absDiffx;
reg [7:0] adds, CoutsAdd;

txtfile = $fopen("C:/Users/andre/OneDrive/Documents/MATLAB/ECSE398/imageMatrix.txt", "r");

// Fill the image matrix from the matrix in the text file i
for(int i = 0; i < 294; i++)
begin
	for(int j = 0; j < 440; j++)
	begin
		$fscanf(txtfile, "%b,", image[i][j]);
	end
end

$fclose(txtfile);

// Perform Roberts Edge Detection on the image matrix and fills edges matrix with results
for(int i = 0; i < 293; i++)
begin
	for(int j = 0; j < 439; j++)
	begin
		//Absolute Difference |image[i][j] - image[i+1][j+1]|
		//image[i][j] - image[i+1][j+1]
		subsAB[0] = image[i][j][0] ^ image[i+1][j+1][0];
		CoutsSubAB[0] = ~image[i][j][0] & image[i+1][j+1][0];
		for(int k = 1; k <= 7; k++)
		begin
			subsAB[k] = (image[i][j][k] ^ image[i+1][j+1][k]) ^ CoutsSubAB[k-1];
			CoutsSubAB[k] = (~image[i][j][k] & image[i+1][j+1][k]) | ((~image[i][j][k] ^ image[i+1][j+1][k]) & (CoutsSubAB[k-1]));
		end
		//image[i+1][j+1] - image[i][j]
		subsBA[0] = image[i+1][j+1][0] ^ image[i][j][0];
		CoutsSubBA[0] = ~image[i+1][j+1][0] & image[i][j][0];
		for(int k = 1; k <= 7; k++)
		begin
			subsBA[k] = (image[i+1][j+1][k] ^ image[i][j][k]) ^ CoutsSubBA[k-1];
			CoutsSubBA[k] = (~image[i+1][j+1][k] & image[i][j][k]) | ((~image[i+1][j+1][k] ^ image[i][j][k]) & (CoutsSubBA[k-1]));
		end
		//Comparator
		grtrA[7] = image[i][j][7] & ~image[i+1][j+1][7];
		grtrB[7] = ~image[i][j][7] & image[i+1][j+1][7];
		for(int k = 6; k >= 0; k--)
		begin
			grtrA[k] = grtrA[k+1] | ~grtrB[k+1] & (image[i][j][k] & ~image[i+1][j+1][k]);
			grtrB[k] = grtrB[k+1] | ~grtrA[k+1] & (~image[i][j][k] & image[i+1][j+1][k]);
		end
		//Final Difference
		for(int k = 0; k <= 7; k++)
		begin
			absDiff[k] = (subsAB[k] & grtrA[0]) | (subsBA[k] & ~grtrA[0]);
		end

		//Absolute Difference |image[i+1][j] - image[j][j+1]|
		//image[i+1][j] - image[i][j+1]
		subsABx[0] = image[i+1][j][0] ^ image[i][j+1][0];
		CoutsSubABx[0] = ~image[i+1][j][0] & image[i][j+1][0];
		for(int k = 1; k <= 7; k++)
		begin
			subsABx[k] = (image[i+1][j][k] ^ image[i][j+1][k]) ^ CoutsSubABx[k-1];
		 	CoutsSubABx[k] = (~image[i+1][j][k] & image[i][j+1][k]) | ((~image[i+1][j][k] ^ image[i][j+1][k]) & CoutsSubABx[k-1]);
		end
		//image[i][j+1] - image[i+1][j]
		subsBAx[0] = image[i][j+1][0] ^ image[i+1][j][0];
		CoutsSubBAx[0] = ~image[i][j+1][0] & image[i+1][j][0];
		for(int k = 1; k <= 7; k++)
		begin
			subsBAx[k] = (image[i][j+1][k] ^ image[i+1][j][k]) ^ CoutsSubBAx[k-1];
			CoutsSubBAx[k] = (~image[i][j+1][k] & image[i+1][j][k]) | ((~image[i][j+1][k] ^ image[i+1][j][k]) & CoutsSubBAx[k-1]);
		end
		//Comparator
		grtrAx[7] = image[i+1][j][7] & ~image[i][j+1][7];
		grtrBx[7] = ~image[i+1][j][7] & image[i][j+1][7];
		for(int k = 6; k >= 0; k--)
		begin
			grtrAx[k] = grtrAx[k+1] | (~grtrBx[k+1] & (image[i+1][j][k] & ~image[i][j+1][k]));
			grtrBx[k] = grtrBx[k+1] | (~grtrAx[k+1] & (~image[i+1][j][k] & image[i][j+1][k]));
		end
		//Final Difference
		for(int k = 0; k <= 7; k++)
		begin
			absDiffx[k] = (subsABx[k] & grtrAx[0]) | (subsBAx[k] & ~grtrAx[0]);
		end

		//Addition
		adds[0] = absDiff[0] ^ absDiffx[0] ^ 1'b0;
		CoutsAdd[0] = (absDiff[0] & absDiffx[0]) | (1'b0 & (absDiff[0] ^ absDiffx[0]));
		for(int k = 1; k <= 7; k++)
		begin
			adds[k] = absDiff[k] ^ absDiffx[k] ^ CoutsAdd[k-1];
			CoutsAdd[k] = (absDiff[k] & absDiffx[k]) | (CoutsAdd[k-1] & (absDiff[k] ^ absDiffx[k]));
		end

		edges[i][j] = adds;
	end
end


outputfile = $fopen("C:/Users/andre/OneDrive/Documents/ECSE398/RobEdge/RobEdgeOp/OutputMatrix.txt", "w");

// Export the edges matrix to a text file
for(int i = 0; i < 292; i++)
begin
	for(int j = 0; j < 438; j++)
	begin
		$fwrite(outputfile, "%b ", edges[i][j]);
	end
	$fwrite(outputfile, "\n");
end

$fclose(outputfile);

end

endmodule