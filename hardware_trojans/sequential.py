import time
import threading
from typing import Callable, Optional

class TrojanCounter:
    def __init__(self, k: int, trigger_kind: str = "all_one", param=None):
        self.k = k
        self.max_value = 1 << k
        self.counter = 0

        self.trigger_kind = trigger_kind
        self.param = param

        # runtime signals
        self.ER = 0      # external input signal
        self.Ena = 1     # enable

        # clock thread control
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._tick_callback: Optional[Callable[[int, int, int], None]] = None
        # callback signature: (cycle_index, counter_value, ER_star)

    # triger condition
    def _trigger(self) -> bool:
        # trigger on all 1s
        if self.trigger_kind == "all_one":
            return self.counter == (self.max_value - 1)
        else:
            raise ValueError("unknown trigger_kind")

    # single clock tick
    def clock_tick(self) -> int:
        """Perform one clock cycle and return ER*."""
        if self.Ena:
            self.counter = (self.counter + 1) % self.max_value

        triggered = self._trigger()

        active = triggered
        ER_star = self.ER ^ int(active)
        return ER_star

    # real time clock
    def _run_clock(self, freq_hz: float, duration_s: Optional[float]):
        """
        Internal: run the clock in a loop at freq_hz Hz.
        If duration_s is provided, run only for that many seconds.
        """
        period = 1.0 / freq_hz if freq_hz > 0 else 0.0
        start = time.time()
        cycle = 0
        while not self._stop_event.is_set():
            tick_time = time.time()
            ER_star = self.clock_tick()
            # call user callback if present
            if self._tick_callback:
                try:
                    self._tick_callback(cycle, self.counter, ER_star)
                except Exception as e:
                    print("Tick callback error:", e)

            cycle += 1
            # stop if duration passed
            if duration_s is not None and (time.time() - start) >= duration_s:
                break

            if period > 0:
                elapsed = time.time() - tick_time
                to_sleep = period - elapsed
                if to_sleep > 0:
                    time.sleep(to_sleep)

    # start clock
    def start_clock(self, freq_hz: float = 1.0, duration_s: Optional[float] = None,
                    callback: Optional[Callable[[int, int, int], None]] = None):
        """
        Start a background thread that ticks at freq_hz and invokes callback.
        callback(cycle_index, counter_value, ER_star)
        If duration_s provided, stops after that many seconds. Otherwise runs until stop_clock().
        """
        if self._thread and self._thread.is_alive():
            raise RuntimeError("Clock already running")

        self._stop_event.clear()
        self._tick_callback = callback
        self._thread = threading.Thread(target=self._run_clock, args=(freq_hz, duration_s), daemon=True)
        self._thread.start()

    def stop_clock(self):
        """Stop the background clock (if running)."""
        if self._thread and self._thread.is_alive():
            self._stop_event.set()
            self._thread.join(timeout=1.0)
        self._thread = None

    # setter methods 
    def set_ER(self, value: int):
        self.ER = 1 if value else 0

    def set_Ena(self, value: int):
        self.Ena = 1 if value else 0

    def set_trigger(self, kind: str, param):
        self.trigger_kind = kind
        self.param = param


# demo callback
def demo_callback(cycle_index, counter_value, ER_star):
    print(f"Cycle {cycle_index:3d}: counter={counter_value:2d}, ER*={ER_star}")

def main():
    k = 4
    # trigger when all 4 bits are 1 (i.e., counter == 2^k - 1 == 15)
    trojan = TrojanCounter(k=k, trigger_kind="all_one")

    # set initial ER and enable
    trojan.set_ER(0)
    trojan.set_Ena(1)

    # Start a real-time clock at 2 Hz for 20 seconds
    trojan.start_clock(freq_hz=2.0, duration_s=20.0, callback=demo_callback)


    # Wait for the background thread to finish (duration_s) or stop manually
    try:
        while trojan._thread and trojan._thread.is_alive():
            time.sleep(0.1)
    except KeyboardInterrupt:
        trojan.stop_clock()
        print("Stopped by user.")

if __name__ == "__main__":
    main()
