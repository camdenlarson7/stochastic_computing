`timescale 1ns / 1ps

module StochasticRobertEdge;

initial
begin

integer txtfile, txtfilesel, outputfile, i, j;
reg [63:0] image[0:293][0:439], edges[0:292][0:438], gradx, grady;
reg selstream[0:293][0:439];

txtfile = $fopen("C:/Users/andre/OneDrive/Documents/MATLAB/ECSE398/bitstreams.txt", "r");

// Fill the image matrix from the matrix in the text file
for(int i = 0; i < 294; i++)
begin
	for(int j = 0; j < 440; j++)
	begin
		$fscanf(txtfile, "%b,", image[i][j]);
	end
end

txtfilesel = $fopen("C:/Users/andre/OneDrive/Documents/MATLAB/ECSE398/selstreams.txt", "r");

// Fill the select bitstream matrix from the matrix in the text file
for(int i = 0; i < 294; i++)
begin
	for(int j = 0; j < 440; j++)
	begin
		$fscanf(txtfilesel, "%b,", selstream[i][j]);
	end
end

// Perform Roberts Edge Detection on the image matrix and fills edges matrix with results
for(int i = 0; i < 293; i++)
begin
	for(int j = 0; j < 439; j++)
	begin
		gradx = image[i][j] ^ image[i+1][j+1];
		grady = image[i][j+1] ^ image[i+1][j];
		edges[i][j] = selstream[i][j] ? gradx : grady;
	end
end

outputfile = $fopen("C:/Users/andre/OneDrive/Documents/ECSE398/RobEdge/RobEdgeOp/StochasticOutputMatrix.txt", "w");

// Export the edges matrix to a text file
for(int i = 0; i < 293; i++)
begin
	for(int j = 0; j < 439; j++)
	begin
		$fwrite(outputfile, "%b ", edges[i][j]);
	end
	$fwrite(outputfile, "\n");
end

$fclose(outputfile);

end

endmodule