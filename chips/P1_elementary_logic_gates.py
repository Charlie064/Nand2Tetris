from chip import Chip

class Nand(Chip):
    """2-input NAND logic gate."""

    def __init__(self, name=None, num_inputs=2, num_outputs=1, input_names=None, output_names=None):
        """Initialise a NAND gate."""
        input_names = input_names or []
        output_names = output_names or []
        super().__init__(name, num_inputs, num_outputs, input_names, output_names)

    def compute(self, inputs):
        """Compute the NAND output for given inputs.

        Args:
            inputs (list[bool] | int): Two boolean inputs [a, b].

        Returns:
            list[bool]: One-element list containing the NAND output.
        """
        inputs = self.input_handling(inputs, 2)
        a, b = inputs
        return [not(a and b)]
            

class Not(Chip):
    """NOT logic gate using a NAND gate."""

    def __init__(self, name=None, num_inputs=1, num_outputs=1, input_names=None, output_names=None):
        """Initialise a NOT gate."""
        input_names = input_names or []
        output_names = output_names or []
        super().__init__(name, num_inputs, num_outputs, input_names, output_names)
        self.nand = Nand()

    def compute(self, input):
        """Compute NOT output for given input.

        Args:
            input (list[bool] | int): Single-element list [a].

        Returns:
            list[bool]: One-element list containing the NOT output.
        """

        input = self.input_handling(input, 1)
        return self.nand.compute(input + input)
    
    def fast_compute(self, input):
        """Compute the NOT output using native Python logic.

        Args:
            inputs (list[bool] | int): Input value.

        Returns:
            list[bool]: Single-element list containing the NOT output.
        """
        input = self.input_handling(input, 1)
        return [not input]


class Or(Chip):
    """2-input OR logic gate implemented using NAND and NOT."""

    def __init__(self, name=None, num_inputs=2, num_outputs=1, input_names=None, output_names=None):
        """Initialise an OR gate using De Morgan's law with NAND/NOT."""
        input_names = input_names or []
        output_names = output_names or []
        super().__init__(name, num_inputs, num_outputs, input_names, output_names)
        self.nand = Nand()
        self._not = Not()

    def compute(self, inputs):
        """Compute OR output using De Morgan's law.

        Args:
            inputs (list[bool] | int): Two boolean inputs [a, b].

        Returns:
            list[bool]: One-element list containing the OR output.
        """
        inputs = self.input_handling(inputs, 2)
        a, b = inputs
        not_a = self._not.compute([a])[0]
        not_b = self._not.compute([b])[0]
        nand_result = self.nand.compute([not_a, not_b])[0]
        return [nand_result]
    
    def fast_compute(self, inputs):
        """Compute OR output using Python `or` for efficiency.

        Args:
            inputs (list[bool] | int): Two boolean inputs [a, b].

        Returns:
            list[bool]: One-element list containing the OR output.
        """
        inputs = self.input_handling(inputs, 2)
        a, b = inputs
        return [a or b]
    

class And(Chip):
    """2-input AND logic gate implemented using NAND and NOT."""

    def __init__(self, name=None, num_inputs=2, num_outputs=1, input_names=None, output_names=None):
        """Initialise an AND gate."""
        input_names = input_names or []
        output_names = output_names or []
        super().__init__(name, num_inputs, num_outputs, input_names, output_names)
        self.nand = Nand()
        self._not = Not()

    def compute(self, inputs):
        """Compute AND output using NAND followed by NOT.

        Args:
            inputs (list[bool] | int): Two boolean inputs [a, b].

        Returns:
            list[bool]: One-element list containing the AND output.
        """
        inputs = self.input_handling(inputs, 2)
        a_nand_b = self.nand.compute(inputs)[0]
        not_result = self._not.compute([a_nand_b])[0]
        return [not_result]
    def fast_compute(self, inputs):
        """Compute AND output using Python `and` for efficiency.

        Args:
            inputs (list[bool] | int): Two boolean inputs [a, b].

        Returns:
            list[bool]: One-element list containing the AND output.
        """
        inputs = self.input_handling(inputs, 2)
        a, b = inputs
        return [a and b]
        

class Xor(Chip):
    """2-input XOR logic gate using combination of AND, OR, NOT, and NAND."""

    def __init__(self, name=None, num_inputs=2, num_outputs=1, input_names=None, output_names=None):
        """Initialise an XOR gate."""
        input_names = input_names or []
        output_names = output_names or []
        super().__init__(name, num_inputs, num_outputs, input_names, output_names)
        self.nand = Nand()
        self._and = And()
        self._not = Not()
        self._or = Or()

    def compute(self, inputs):
        """Compute XOR output using formula a(~b) + (~a)b.

        Args:
            inputs (list[bool] | int): Two boolean inputs [a, b].

        Returns:
            list[bool]: One-element list containing the XOR output.
        """
        inputs = self.input_handling(inputs, 2)
        a, b = inputs
        not_a = self._not.compute([a])[0]
        not_b = self._not.compute([b])[0]
        only_a = self._and.compute([a, not_b])[0]
        only_b = self._and.compute([not_a, b])[0]
        or_result = self._or.compute([only_a, only_b])[0]
        return [or_result]
    
    def fast_compute(self, inputs):
        """Compute XOR output using Python `^` for efficiency.

        Args:
            intputs (list[bool | int): Two boolean inputs [a, b].

        Returns:
            list[bool]: One-element list containing the XOR output.
        """

        a, b = inputs
        return [a ^ b]


class Mux(Chip):
    """Represents a 2-to-1 multiplexer using AND, OR, and NOT."""

    def __init__(self, name=None, num_inputs=3, num_outputs=1, input_names = ["sel", "a", "b"], output_names=None):
        """Initialise a MUX."""
        input_names = input_names or []
        output_names = output_names or []
        super().__init__(name, num_inputs, num_outputs, input_names, output_names)
        self._and = And()
        self._not = Not()
        self._or = Or()

    def compute(self, inputs):
        """Compute MUX output: (-sel)a + (sel)b.

        Args:
            intputs (list[bool | int): Three boolean inputs [sel, a, b].

        Returns:
            list[bool]: One-element list containing the selected output.
        """
        inputs = self.input_handling(inputs, 3, "(sel, a, b)")
        sel, a, b = inputs
        not_sel = self._not.compute([sel])[0]
        sel_a = self._and.compute([not_sel, a])[0]
        sel_b = self._and.compute([sel, b])[0]
        or_result = self._or.compute([sel_a, sel_b])[0]
        return [or_result]
    
    def fast_compute(self, inputs):
        """Compute MUX output using Python `if` for efficiency.

        Args:
            intputs (list[bool | int): Three boolean inputs [sel, a, b].

        Returns:
            list[bool]: One-element list containing the selected output.
        """
        sel, a, b = inputs
        return [b] if sel else [a]


class Dmux(Chip):
    """Represents a 1-to-2 demultiplexer using AND, NOT."""

    def __init__(self, name=None, num_inputs=2, num_outputs=2, input_names = ["sel", "input"], output_names=["out1", "out2"]):
        """Initialise a DMUX."""
        input_names = input_names or []
        output_names = output_names or []
        super().__init__(name, num_inputs, num_outputs, input_names, output_names)
        self._and = And()
        self._not = Not()

    def compute(self, inputs):
        """Compute DMUX outputs.

        Args:
            intputs (list[bool | int): Two boolean inputs [sel, input].

        Returns:
            list[bool]: Two-element list containing [output1, output2].
        """
        inputs = self.input_handling(inputs, 2, "(1 select, 1 input)")
        sel, input = inputs
        # output_1 = (-sel)(input)
        # output_2 = (sel)(input)
        not_sel = self._not.compute([sel])[0]
        sel_out_1 = self._and.compute([not_sel, input])[0]
        sel_out_2 = self._and.compute([sel, input])[0]
        return [sel_out_1, sel_out_2]
    
    def fast_compute(self, inputs):
        """Compute DMUX outputs using Python logic for efficiency.

        Args:
            intputs (list[bool | int): Two boolean inputs [input, sel].

        Returns:
            list[bool]: Two-element list containing [output1, output2].
        """
        inputs = self.input_handling(inputs, 2, "(1 input, 1 select)")
        input, sel = inputs
        return [False, input] if sel else [input, False]



if __name__ == "__main__":
    """Example usecases"""  

    dmux = Dmux()
    dmux_input = True
    dmux_sel = True
    print(f"Dmux test. Select = {dmux_sel}, Input = {dmux_input}, Output: {dmux.compute([dmux_sel, dmux_input])}")

    mux = Mux()
    mux_input_1 = True
    mux_input_2 = False
    mux_sel = True
    print(f"Mux test. Select = {mux_sel}, Input 1 = {mux_input_1}, Input 2 = {mux_input_2}, Output: {mux.compute([mux_sel, mux_input_1, mux_input_2])}")

    the_chips_in_which_I_would_appreciate_the_exquisite_honour_of_testing = [Nand, Not, Or, And, Xor, Mux, Dmux]
    for chip in the_chips_in_which_I_would_appreciate_the_exquisite_honour_of_testing:
        test = chip()
        test.truth_table()
    
