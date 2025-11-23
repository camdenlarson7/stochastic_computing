module BinaryTrojanRobertEdge;

initial
begin

integer txtfile, outputfile;
integer i, j, k;
reg [7:0] image[0:293][0:439], edges[0:292][0:438];
reg [7:0] subsAB, subsBA, CoutsSubAB, CoutsSubBA, grtrA, grtrB, absDiff;
reg [7:0] subsABx, subsBAx, CoutsSubABx, CoutsSubBAx, grtrAx, grtrBx, absDiffx;
reg [7:0] adds, CoutsAdd;

// Example Trojan configuration
localparam int TROJAN_COL_START = 150;   // j >= Trojan can activate
localparam int TROJAN_COL_END   = 350;   // j <  Trojan active region
localparam [7:0] TROJAN_CONST  = 8'hA5;  // example constant payload


// Payload modes
localparam int MODE_FORCE_0 = 0;
localparam int MODE_FORCE_1 = 1;
localparam int MODE_FLIP    = 2;
localparam int MODE_CONST   = 3;


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

		// Hardware Trojan on the adder output
    	reg       trojan_active;
    	integer   payload_mode;
    	reg [7:0] normal_edge;
    	reg [7:0] bit_mask;      // dynamic mask
    	integer   bit_index;     // which bit to hit 0..7

    	normal_edge = adds;  // "honest" Roberts magnitude

    	// Sequential trigger: Trojan only active in certain columns
    	trojan_active = (j >= TROJAN_COL_START) && (j < TROJAN_COL_END);

    	// Choose which bit position to corrupt for this pixel based on row
    	bit_index = (i * j) % 8;

    	// Create a mask with a 1 at bit_index, 0 elsewhere
    	bit_mask = 8'b0000_0001 << bit_index;

    	// Payload selection based on row i (four horizontal bands)
    	if (i < 73)
    	    payload_mode = MODE_FORCE_0;
    	else if (i < 146)
    	    payload_mode = MODE_FORCE_1;
    	else if (i < 219)
    	    payload_mode = MODE_FLIP;
    	else
    	    payload_mode = MODE_CONST;

    	// Apply Trojan: only modify the bit chosen by bit_mask
    	if (!trojan_active) begin
    	    edges[i][j] = normal_edge;
    	end
    	else begin
    	    case (payload_mode)
    	        MODE_FORCE_0: edges[i][j] =
    	            normal_edge & ~bit_mask;                  // force that bit to 0

    	        MODE_FORCE_1: edges[i][j] =
    	            normal_edge | bit_mask;                   // force that bit to 1

    	        MODE_FLIP:    edges[i][j] =
    	            normal_edge ^ bit_mask;                   // flip that bit

    	        MODE_CONST:   edges[i][j] =
    	            (normal_edge & ~bit_mask) | (TROJAN_CONST & bit_mask);
    	                                                       // take that bit from TROJAN_CONST
    	        default:      edges[i][j] = normal_edge;
    	    endcase
    	end
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