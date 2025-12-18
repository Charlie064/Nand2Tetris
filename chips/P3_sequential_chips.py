from P1_elementary_logic_gates import * 
from clock import *

class DFF(Chip):
    """
    D flip-flop (positive edge triggered).

    On a rising clock edge, the value on D is stored internally.
    The stored value is exposed as Q, with QB = ~Q.
    """
    def __init__(self, name=None, num_inputs=1, num_outputs=2, input_names = None, output_names=None):
        """
        Initialize the D flip-flop.

        The clock is not treated as a logical input; it is supplied
        externally by the Clock via on_clock().
        """

        input_names = input_names or ["D"]
        output_names = output_names or ["Q", "QB"]
        super().__init__(name, num_inputs, num_outputs, input_names, output_names)

        self.D = False
        self.q = False
        self.prev_clk = False
    

    def set_input(self, D):
        """
        Set the D input value.

        Args:
            D (bool | int): Input value to be latched on the next rising clock edge.
        """

        self.D = bool(D)


    def compute(self):
        """
        Expose the current outputs of the flip-flop.

        Returns:
            list[bool]: [Q, ~Q]
        """
        return [self.q, not self.q]
    

    def on_clock(self, clk):
        """
        Update the flip-flop state based on the clock.

        On a rising edge, latch D into Q.

        Args:
            clk (bool | int): Current clock level.
        """

        clk = bool(clk)        
        # Rising edge detection

        if not self.prev_clk and clk:
            self.q = self.D
        self.prev_clk = clk
    


if __name__ == "__main__":
    """Example usecases"""

    clock = Clock()
    dff = DFF()
    clock.subscribe([dff])
    
    D, Q = dff.compute()
    print(f"D: {D}, Q: {Q}")

    dff.set_input(1)
    clock.tick()
    D, Q = dff.compute()
    print(f"D: {D}, Q: {Q}")

    dff.set_input(0)
    clock.tick()
    D, Q = dff.compute()
    print(f"D: {D}, Q: {Q}")

        
