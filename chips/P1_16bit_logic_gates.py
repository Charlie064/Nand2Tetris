from P1_elementary_logic_gates import *


class NotN(Chip):
    """N-bit NOT gate implemented using N single-bit NOT gates."""
    def __init__(self, num_bits, name=None, input_names=None, output_names=None):
        self.num_bits = num_bits
        num_inputs = num_bits
        num_outputs = num_bits
        input_names = input_names or [f"in{i}" for i in range(num_bits)]
        output_names = output_names or [f"out{i}" for i in range(num_bits)]
        super().__init__(name, num_inputs, num_outputs, input_names, output_names)
        self._not = Not()

    def compute(self, inputs):
        """
        Compute the N-bit NOT operation.

        Args:
            input (list[bool] | int): N-bit boolean list or integer to invert.

        Returns:
            list[bool]: Bitwise negation of the input.
        """   
        inputs = self.input_handling(inputs, self.num_inputs)
        return [self._not.compute([bit])[0] for bit in inputs]


class AndN(Chip):
    """N-bit bitwise AND gate implemented using N single-bit AND gates."""
    def __init__(self, num_bits, name=None, input_names=None, output_names=None):
        self.num_bits = num_bits
        num_inputs = 2 * num_bits
        num_outputs = num_bits
        input_names = input_names or [f"in{j}_{i}" for j in range(2) for i in range(num_bits)]
        output_names = output_names or [f"out{i}" for i in range(num_bits)]
        super().__init__(name, num_inputs, num_outputs, input_names, output_names)
        self._and = And()

    def compute(self, inputs):
        """
        Compute the N-bit AND operation.

        Args:
            input (list[bool] | int): 2*N-bit boolean list or integer.

        Returns:
            list[bool]: Bitwise AND of the two inputs.
        """   
        inputs = self.input_handling(inputs, self.num_inputs)
        x = inputs[:self.num_bits]
        y = inputs[self.num_bits:]
        return [self._and.compute([x[bit], y[bit]])[0] for bit in range(self.num_bits)]
    

class OrN(Chip):
    """N-bit bitwise OR gate implemented using N single-bit OR gates."""
    def __init__(self, num_bits, name=None, input_names=None, output_names=None):
        self.num_bits = num_bits
        num_inputs = 2 * num_bits
        num_outputs = num_bits
        input_names = input_names or [f"in{j}_{i}" for j in range(2) for i in range(num_bits)]
        output_names = output_names or [f"out{i}" for i in range(num_bits)]
        super().__init__(name, num_inputs, num_outputs, input_names, output_names)
        self._or = Or()

    def compute(self, inputs):
        """
        Compute the N-bit OR operation.

        Args:
            input (list[bool] | int): 2*N-bit boolean list or integer.

        Returns:
            list[bool]: Bitwise OR of the two inputs.
        """
        inputs = self.input_handling(inputs, self.num_inputs)
        x = inputs[:self.num_bits]
        y = inputs[self.num_bits:]
        return [self._or.compute([x[bit], y[bit]])[0] for bit in range(self.num_bits)]


class MuxN(Chip):
    """N-bit multiplexer implemented using N single-bit multiplexers."""
    def __init__(self, num_bits, name=None, input_names=None, output_names=None):
        self.num_bits = num_bits
        num_inputs = 1 + 2 * num_bits  # 1 select bit + two N-bit inputs
        num_outputs = num_bits
        input_names = input_names or ["sel"] + [f"in{way}_{i}" for way in range(2) for i in range(num_bits)]
        output_names = output_names or [f"out{i}" for i in range(num_bits)]
        super().__init__(name, num_inputs, num_outputs, input_names, output_names)
        self._mux = Mux()
    def compute(self, inputs):
        """
        Compute the N-bit MUX operation.

        Args:
            input (list[bool] | int): 1-bit select signal followed by two N-bit inputs
                                    (total 1 + 2*N bits).

        Returns:
            list[bool]: Bitwise selected output from input 1 or input 2.
        """        
        inputs = self.input_handling(inputs, self.num_inputs, "(1 sel + N-bit in1 + N-bit in2)")
        sel = inputs[0]
        x = inputs[1:self.num_bits + 1]
        y = inputs[self.num_bits + 1:]
        return [self._mux.compute([sel, x[bit], y[bit]])[0] for bit in range(self.num_bits)]
    


if __name__ == "__main__":
    """Example usecases"""

    mux16 = MuxN(16)
    mux16_inputs_x = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    mux16_inputs_y = [0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1]
    sel = [1]
    print(f" Mux16 test. Select = {sel}, Input 1 = {mux16_inputs_x}, Input 2 = {mux16_inputs_y}, Output: {mux16.compute(sel + mux16_inputs_x + mux16_inputs_y)}")


    not16 = NotN(16)
    inputs = [1,1,0,1,0,0,1,0,1,1,1,1,1,1,1,1]
    print(f" Not16 test. Input = {inputs}, Output: {not16.compute(inputs)}")


    chips_I_want_to_test = [NotN(5), AndN(5), OrN(5), MuxN(5)]
    for chip in chips_I_want_to_test:
        chip.truth_table()