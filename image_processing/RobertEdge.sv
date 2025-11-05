module RobertEdge;

initial
begin

integer txtfile;
integer outputfile;
integer i, j;
reg [7:0] image[0:293][0:439];
reg [7:0] edges[0:292][0:438];

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
		int gradx, grady, absgradx, absgrady;
		gradx = image[i][j] - image[i+1][j+1];
		grady = image[i][j+1] - image[i+1][j];
		absgradx = gradx;
		absgrady = grady;
		if(gradx < 0)
			absgradx = - gradx;
		if(grady < 0)
			absgrady = - grady;
		edges[i][j] = absgradx + absgrady;
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

end

endmodule