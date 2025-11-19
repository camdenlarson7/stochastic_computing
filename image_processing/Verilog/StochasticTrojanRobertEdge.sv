`timescale 1ns / 1ps

module StochasticRobertEdge;

initial
begin

// Example Trojan configuration (can tune these for testing)
localparam int TROJAN_COL_START = 150;   // j >= Trojan can activate
localparam int TROJAN_COL_END   = 350;   // j <  Trojan active region

// Payload modes
localparam int MODE_FORCE_0 = 0;
localparam int MODE_FORCE_1 = 1;
localparam int MODE_FLIP    = 2;
localparam int MODE_CONST   = 3;

// Example constant Trojan bitstream (can be any 64-bit pattern)
reg [63:0] trojan_const = 64'hA5A5_5A5A_F0F0_0F0F;

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
for (int i = 0; i < 293; i++) begin
  for (int j = 0; j < 439; j++) begin
    reg [63:0] gradx, grady;
    reg [63:0] normal_edge;
    int        payload_mode;
    bit        trojan_active;

    // Normal Roberts computation
    gradx       = image[i][j]   ^ image[i+1][j+1];
    grady       = image[i][j+1] ^ image[i+1][j];
    normal_edge = selstream[i][j] ? gradx : grady;

    // Sequential trigger based on j (acts like a time/column counter)
    trojan_active = (j >= TROJAN_COL_START) && (j < TROJAN_COL_END);

    // Payload selection based on i
    // Split the image vertically into 4 bands with different Trojan effects
    if (i < 73) begin
      payload_mode = MODE_FORCE_0;   // band 1: force 0
    end
    else if (i < 146) begin
      payload_mode = MODE_FORCE_1;   // band 2: force 1
    end
    else if (i < 219) begin
      payload_mode = MODE_FLIP;      // band 3: flip
    end
    else begin
      payload_mode = MODE_CONST;     // band 4: constant Trojan value
    end

    // Apply Trojan at the output of the operation
    if (!trojan_active) begin
      // Trojan dormant: honest Roberts edge result
      edges[i][j] = normal_edge;
    end
    else begin
      // Trojan active: corrupt normal_edge according to payload_mode
      case (payload_mode)
        MODE_FORCE_0: edges[i][j] = '0;                // all zeros
        MODE_FORCE_1: edges[i][j] = ~'0;               // all ones
        MODE_FLIP:    edges[i][j] = ~normal_edge;      // bitwise invert
        MODE_CONST:   edges[i][j] = trojan_const;      // fixed Trojan pattern
        default:      edges[i][j] = normal_edge;       // safety fallback
      endcase
    end
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