from P3_sequential_chips import *

class Clock:
    """
    Global clock signal generator.

    Drives all subscribed sequential chips by toggling
    the clock level and notifying them of clock edges.
    """    
    def __init__(self):
        self.time = 0
        self.clk_lvl = False
        self.subscribers = []

    def subscribe(self, chips):
        """
        Subscribe sequential chips to this clock.

        Args:
            chips (list): List of sequential chip instances.
        """

        for chip in chips:
            self.subscribers.append(chip)


    def tick(self):
        """
        Advance the clock by one full cycle.
        Subscribed chips are notified on both rising and falling edges.
        """

        # Rising edge
        self.clk_lvl = True
        for chip in self.subscribers:
            chip.on_clock(self.clk_lvl)

        # Falling edge
        self.clk_lvl = False
        for chip in self.subscribers:
            chip.on_clock(self.clk_lvl)

        self.time += 1





if __name__ == "__main__":
    dff = DFF()
    clk = Clock([dff])
    print(dff.compute([False]))
    clk.tick()
    print(dff.compute())
