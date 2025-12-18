from P1_elementary_logic_gates import * 
from clock import *
from chip import *

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
        self.Q = False
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
        return [self.Q, not self.Q]
    

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
            self.Q = self.D
        self.prev_clk = clk
    

class Bit(Chip):
    """
    1-bit register with load control.

    If load == 1, stores input on next rising clock edge.
    If load == 0, retains previous value.
    """

    def __init__(self, name=None, num_inputs=2, num_outputs=1, input_names = None, output_names=None):
        input_names = input_names or ["in, load"]
        output_names = output_names or ["out"]

        super().__init__(name, num_inputs, num_outputs, input_names, output_names)
        self.mux = Mux()
        self.dff = DFF()
        self.in_val = False
        self.load = False


    def set_input(self, inputs):
        """
        Set input and load signal.

        Args:
            inputs (list[bool]): [in, load]
        """
        self.input, self.load = self.input_handling(inputs, 2, "1 input, 1 load")
        current_Q, _ = self.dff.compute()
        next_D = self.mux.compute([self.load, current_Q, self.input])[0]
        self.dff.set_input(next_D)


    def compute(self):
        """
        Return current stored bit.

        Returns:
            list[bool]: [out]
        """
        Q, _ = self.dff.compute()
        return [Q]
    

    def on_clock(self, clk):
        """
        Forward clock to internal DFF.

        Args:
            clk (bool | int): Current clock level.
        """
        self.dff.on_clock(clk)


class RegisterN(Chip):
    """
    N-bit register with load control.

    If load == 1, stores input on next rising clock edge.
    If load == 0, retains previous value.
    """

    def __init__(self,  num_bits=16, name=None, input_names = None, output_names=None):
        self.num_bits = num_bits
        num_inputs = num_bits + 1
        num_outputs = num_bits 
        input_names = input_names or [f"in_{i}" for i in range(num_bits)] + ["load"]
        output_names = output_names or [f"out_{i}" for i in range(num_bits)]

        super().__init__(name, num_inputs, num_outputs, input_names, output_names)
        self.bits = [Bit(name=f"bit_{i}") for i in range(num_bits)]
        self.in_vals = [False]*num_bits
        self.load = False


    def set_input(self, inputs):
        inputs = self.input_handling(inputs, self.num_inputs, "(N-inputs, 1 load)")
        self.in_vals = inputs[:-1]
        load = inputs[-1]
        """
        Set inputs and load signal.

        Args:
            inputs (list[bool]): [in_0, in_1, ..., in_{N-1}, load]
        """
        for i in range(self.num_bits):
            self.bits[i].set_input([self.in_vals[i], load])


    def compute(self):
        """
        Return current stored value of the register.

        Returns:
            list[bool]: N-bit output
        """
        return [bit.compute()[0] for bit in self.bits]
    

    def on_clock(self, clk):
        """
        Forward clock to internal bits.

        Args:
            clk (bool | int): Current clock level.
        """
        for bit in self.bits:
            bit.on_clock(clk)



if __name__ == "__main__":
    """Example usecases"""

    clock = Clock()
    register16 = RegisterN(16)
    clock.subscribe([register16])
    input = 0b1100000000000001
    input = int_to_bool_list(input)
    load = [False]

    # Current output state
    out = register16.compute()
    print(f"Out = {out}")

    # Change input, do not load

    register16.set_input(input + load)
    print(f"Input = {input}, load = {load}")

    # Output doesn't change when ticked since load is False.
    clock.tick()
    out = register16.compute()
    print(f"Out = {out}")

    # Change input, DO load
    load = [True]
    register16.set_input(input + load)
    print(f"Input = {input}, load = {load}")

    # Output changes when ticked since load is True.
    clock.tick()
    out = register16.compute()
    print(f"Out = {out}")
