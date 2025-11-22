`timescale 1ns / 1ps

module StochasticTrojanRobertEdge;

initial
begin

// Example Trojan configuration (can tune these for testing)
localparam int TROJAN_COL_START = 150;   // j >= Trojan can activate
localparam int TROJAN_COL_END   = 350;   // j <  Trojan active region

// Bit mask for payload application
localparam [63:0] BIT_MASK = 64'h0101_0101_0101_0101;

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

    // Trigger: Trojan active in specified column range
    trojan_active = (j >= 150) && (j < 350);

    // Payload selection based on i
    if (i < 73)
      payload_mode = MODE_FORCE_0;
    else if (i < 146)
      payload_mode = MODE_FORCE_1;
    else if (i < 219)
      payload_mode = MODE_FLIP;
    else
      payload_mode = MODE_CONST;

    // To use a single payload mode for all bits
    payload_mode = MODE_FLIP;

    // Apply Trojan at the output on specified bits
    if (!trojan_active) begin
      edges[i][j] = normal_edge;
    end
    else begin
      case (payload_mode)
        // Force 0 only on masked bits
        MODE_FORCE_0: edges[i][j] =
          normal_edge & ~BIT_MASK;

        // Force 1 only on masked bits
        MODE_FORCE_1: edges[i][j] =
          normal_edge | BIT_MASK;

        // Flip only masked bits
        MODE_FLIP:    edges[i][j] =
          normal_edge ^ BIT_MASK;

        // Replace masked bits with Trojan constant bits
        MODE_CONST:   edges[i][j] =
          (normal_edge & ~BIT_MASK) | (trojan_const & BIT_MASK);
        default:      edges[i][j] = normal_edge;
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