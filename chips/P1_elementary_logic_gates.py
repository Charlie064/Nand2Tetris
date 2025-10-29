from chip import Chip


class Nand(Chip):
    def __init__(self, name=None, num_inputs=2, num_outputs=1, input_names = [], output_names=[]):
        super().__init__(name, num_inputs, num_outputs, input_names, output_names)
    def compute(self, x, y):
        return not(x and y)
            

class Not(Chip):
    def __init__(self, name=None, num_inputs=1, num_outputs=1, input_names = [], output_names=[]):
        super().__init__(name, num_inputs, num_outputs, input_names, output_names)
        self.nand = Nand()
    def compute(self, x):
        return self.nand.compute(x,x)
    def fast_compute(self, x):
        return not x


class Or(Chip):
    def __init__(self, name=None, num_inputs=2, num_outputs=1, input_names = [], output_names=[]):
        super().__init__(name, num_inputs, num_outputs, input_names, output_names)
        self.nand = Nand()
        self._not = Not()
    def compute(self, x, y):
        # De Morgan Law
        not_x = self._not.compute(x)
        not_y = self._not.compute(y)
        return self.nand.compute(not_x, not_y)
    def fast_compute(self, x, y):
        return (x or y)
    

class And(Chip):
    def __init__(self, name=None, num_inputs=2, num_outputs=1, input_names = [], output_names=[]):
        super().__init__(name, num_inputs, num_outputs, input_names, output_names)
        self.nand = Nand()
        self._not = Not()
    def compute(self, x, y):
        x_nand_y = self.nand.compute(x, y)
        return self._not.compute(x_nand_y)
    def fast_compute(self, x, y):
        return (x and y)
        

class Xor(Nand):
    def __init__(self, name=None, num_inputs=2, num_outputs=1, input_names = [], output_names=[]):
        super().__init__(name, num_inputs, num_outputs, input_names, output_names)
        self.nand = Nand()
        self._and = And()
        self._not = Not()
        self._or = Or()
    def compute(self, x, y):
        #  x(~y) + (~x)y
        not_x = self._not.compute(x)
        not_y = self._not.compute(y)
        only_x = self._and.compute(x, not_y)
        only_y = self._and.compute(not_x, y)
        return self._or.compute(only_x, only_y)
    def fast_compute(self, x, y):
        return (x ^ y)


class Mux(Chip):
    def __init__(self, name=None, num_inputs=3, num_outputs=1, input_names = ["a", "b", "sel"], output_names=[]):
        super().__init__(name, num_inputs, num_outputs, input_names, output_names)
        self._and = And()
        self._not = Not()
        self._or = Or()
    def compute(self, x, y, sel):
        # mux = (-sel)x + (sel)y
        not_sel = self._not.compute(sel)
        sel_x = self._and.compute(not_sel, x)
        sel_y = self._and.compute(sel, y)
        return self._or.compute(sel_x, sel_y)
    def fast_compute(self, x, y, sel):
        if sel:
            return y
        else:
            return x


class Dmux(Chip):
    def __init__(self, name=None, num_inputs=2, num_outputs=2, input_names = ["input", "sel"], output_names=["out1", "out2"]):
        super().__init__(name, num_inputs, num_outputs, input_names, output_names)
        self._and = And()
        self._not = Not()
        self._or = Or()
    def compute(self, input, sel):
        # output_1 = (-sel)(input)
        # output_2 = (sel)(input)
        not_sel = self._not.compute(sel)
        sel_out_1 = self._and.compute(not_sel, input)
        sel_out_2 = self._and.compute(sel, input)
        return [sel_out_1, sel_out_2]
    def fast_compute(self, input, sel):
        if sel:
            return [False, input]
        else:
            return [input, False]



def int_to_bool_list(value, bits=16):
    """Converts binary to list"""
    # Move bits (in decending order from MSB to LSB) to LSB
    # & 1 = 1 checks if the new LSB is 1
    return [((value >> i) & 1 == 1) for i in reversed(range(bits))]


if __name__ == "__main__":
    chips_I_want_to_test = [Nand, Not, Or, And, Xor, Mux, Dmux]
    for chip in chips_I_want_to_test:
        test = chip()
        test.truth_table()
