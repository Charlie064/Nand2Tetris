from P1_elementary_logic_gates import *
from P1_16bit_logic_gates import *



class Or8Way(Chip):
    """8-input OR gate."""
    def __init__(self, name=None, num_inputs=8, num_outputs=1, input_names = None, output_names=None):
        input_names = input_names or [f"in_{i}" for i in range(8)]
        output_names = output_names or ["out"]
        super().__init__(name, num_inputs, num_outputs, input_names, output_names)
        self._or = Or()

    def compute(self, inputs):
        """
        Compute Or8Way output.

        Args:
            input (list[bool] | int): 8-bit boolean list or integer to invert.

        Returns:
            list[bool]: 8-bit bitwise computation.
        """   
        inputs = self.input_handling(inputs, self.num_inputs)
        _or_1 = self._or.compute(inputs[0:2])[0]
        _or_2 = self._or.compute(inputs[2:4])[0]
        _or_3 = self._or.compute(inputs[4:6])[0]
        _or_4 = self._or.compute(inputs[6:8])[0]
        _or_5 = self._or.compute([_or_1, _or_2])[0]
        _or_6 = self._or.compute([_or_3, _or_4])[0]
        return self._or.compute([_or_5, _or_6])
    

class Mux4Way16(Chip):
    """Represents a 16-bit 8 input multiplexor."""

    def __init__(self, name=None, num_inputs=16*4+2, num_outputs=16, input_names = None, output_names=None):
        """Initialise a Mux4Way16."""
        input_names = input_names or ["sel0", "sel1"] + [f"in{way_j}_{i}" for way_j in range(4) for i in range(16)]
        output_names = output_names or [f"out{i}" for i in range(16)]   
        super().__init__(name, num_inputs, num_outputs, input_names, output_names)
        self.mux16 = MuxN(16)

    def compute(self, inputs): 
        """
        Compute Mux4Way16 outputs.

        Args:
            inputs (list[bool] | int): 2 sel + 16-inp/way * 4 way boolean inputs: [sel0, sel1] + (way_i[:16] for i in range(4))

        Returns:
            list[bool]: Sixteen-element list containing [out_bit_0, out_bit_1, ... , out_bit_15].
        """
        inputs = self.input_handling(inputs, self.num_inputs, "(2 sel, 16-bit inputs per way * 4 ways)")
        s0, s1 = inputs[:2]
        inputs_1 = inputs[2:18]
        inputs_2 = inputs[18:34]
        inputs_3 = inputs[34:50]
        inputs_4 = inputs[50:66]
        mux_0 = self.mux16.compute([s0] + inputs_1 + inputs_2)
        mux_1 = self.mux16.compute([s0] + inputs_3 + inputs_4)
        return self.mux16.compute([s1] + mux_0 + mux_1)
    

class Mux8Way16(Chip):
    """Represents a 16-bit 8 input multiplexor."""

    def __init__(self, name=None, num_inputs=16*8+3, num_outputs=16, input_names = None, output_names=None):
        """Initialise a Mux8Way16."""
        input_names = input_names or ["sel0", "sel1", "sel2"] + [f"in{way_j}_{i}" for way_j in range(8) for i in range(16)]
        output_names = output_names or [f"out{i}" for i in range(16)]   
        super().__init__(name, num_inputs, num_outputs, input_names, output_names)
        self.mux16 = MuxN(16)
        self.mux4way16 = Mux4Way16()

    def compute(self, inputs): 
        """Compute Mux8Way16 outputs.

        Args:
            inputs (list[bool] | int): 3 sel + 16-inp/way * 8 way boolean inputs: [sel0, sel1, sel2] + (way_i[:16] for i in range(8))

        Returns:
            list[bool]: Sixteen-element list containing [out_bit_0, out_bit_1, ... , out_bit_15].
        """
        inputs = self.input_handling(inputs, self.num_inputs, "(3 sel, 16-inp/way * 8 way)")
        s0, s1, s2 = inputs[:3]
        inputs_1 = inputs[3:19]
        inputs_2 = inputs[19:35]
        inputs_3 = inputs[35:51]
        inputs_4 = inputs[51:67]
        inputs_5 = inputs[67:83]
        inputs_6 = inputs[83:99]
        inputs_7 = inputs[99:115]
        inputs_8 = inputs[115:131]

        mux_0 = self.mux4way16.compute([s0, s1] + inputs_1 + inputs_2 + inputs_3 + inputs_4)
        mux_1 = self.mux4way16.compute([s0, s1] + inputs_5 + inputs_6 + inputs_7 + inputs_8)
        return self.mux16.compute([s2] + mux_0 + mux_1)


class DMux4Way(Chip):
    """Represents a 1-to-4 demultiplexer."""

    def __init__(self, name=None, num_inputs=3, num_outputs=4, input_names = None, output_names = None):
        """Initialise a DMux4Way."""
        input_names = input_names or ["sel0", "sel1", "input"]
        output_names = output_names or [f"out{i}" for i in range(4)]
        super().__init__(name, num_inputs, num_outputs, input_names, output_names)
        self.dmux = Dmux()


    def compute(self, inputs):
        """Compute DMux4Way outputs.

        Args:
            inputs (list[bool] | int): 3-bit boolean int or list [sel0, sel1, input].

        Returns:
            list[bool]: Four-element list containing [out0, out1, out2, out3].
        """
        inputs = self.input_handling(inputs, 3, "(2 select, 1 input)")
        s0, s1, input = inputs
        output_0_mux, output_1_mux = self.dmux.compute([s1, input])
        output_0, output_1 = self.dmux.compute([s0, output_0_mux])
        output_2, output_3 = self.dmux.compute([s0, output_1_mux])
        return [output_0, output_1, output_2, output_3]


class DMux8Way(Chip):
    """Represents a 1-to-8 demultiplexer."""

    def __init__(self, name=None, num_inputs=4, num_outputs=4, input_names = ["sel0", "sel1", "sel2", "input"], output_names = [f"out{i}" for i in range(8)]):
        """Initialise a DMux8Way."""
        input_names = input_names or []
        output_names = output_names or []
        super().__init__(name, num_inputs, num_outputs, input_names, output_names)
        self.dmux4way = DMux4Way()
        self.dmux = Dmux()
    def compute(self, inputs):
        """Compute DMux8Way outputs.

        Args:
            inputs (list[bool] | int): 4-bit boolean input or list [sel0, sel1, sel2, input].

        Returns:
            list[bool]: Eight-element list containing [out0, out1, out2, out3, out4, out5, out6, out7].
        """
        inputs = self.input_handling(inputs, 4, "(3 select, 1 input)")
        s0, s1, s2, input = inputs
        dmux_0, dmux_1 = self.dmux.compute([s2, input])
        outputs_0_to_3 = self.dmux4way.compute([s0, s1, dmux_0])
        outputs_4_to_7 = self.dmux4way.compute([s0, s1, dmux_1])
        return outputs_0_to_3 + outputs_4_to_7

if __name__ == "__main__":
    """Example usecases"""
    
    _or8way = Or8Way()
    inputs = [0,0,0,0,0,0,0,0]
    print(f" Or8Way test. Inputs = {inputs}, Output: {_or8way.compute(inputs)}")

    mux8way16 = Mux8Way16()
    mux4way16 = Mux4Way16()
    dmux4way = DMux4Way()
    dmux8way = DMux8Way()

    inputs_1 = [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0]
    inputs_2 = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    inputs_3 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    inputs_4 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1]
    inputs_5 = [0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1]
    inputs_6 = [0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1]
    inputs_7 = [0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1]
    inputs_8 = [0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1]

    select = [0,1] # input 3
    inputs = select + inputs_1 + inputs_2 + inputs_3 + inputs_4
    print(f" Mux4Way16 test, Output: {mux4way16.compute(inputs)}")

    select = [0,1,1] # input 7
    inputs = select + inputs_1 + inputs_2 + inputs_3 + inputs_4 + inputs_5 + inputs_6 + inputs_7 + inputs_8
    print(f" Mux8Way16 test, Output: {mux8way16.compute(inputs)}")


    chips_I_want_to_test = [Or8Way, DMux4Way, DMux8Way]
    for chip in chips_I_want_to_test:
        test = chip()
        test.truth_table()