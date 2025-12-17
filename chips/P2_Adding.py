from P1_elementary_logic_gates import *
from P1_16bit_logic_gates import *
from chip import *


class HalfAdder(Chip):
    """Half adder implemented using one XOR gate and one AND gate."""
    def __init__(self, name=None, num_inputs=2, num_outputs=2, input_names = None, output_names=None):
        output_names = ["sum", "c_out"] 
        super().__init__(name, num_inputs, num_outputs, input_names, output_names)
        self._and = And()
        self._xor = Xor()

    def compute(self, inputs):
        """
        Compute the half-adder result.

        Args:
            inputs (list[bool] | int): Two input bits [a, b].

        Returns:
            list[bool]: [sum, carry_out].
        """
        inputs = self.input_handling(inputs, self.num_inputs)
        carry_out = self._and.compute(inputs)[0]
        sum = self._xor.compute(inputs)[0]    
        return [sum, carry_out]


class FullAdder(Chip):
    """
    Full adder implemented using two half adders and one OR gate.

    Derivation:

    sum = ~a~bc + ~ab~c + abc + a~b~c 
    = a(bc + ~b~c) + ~a(~bc + b~c)
    =>  
        { first term: bc + ~b~c = ~~(bc + ~b~c) = {deMorgan}
        = ~((~b + ~c) + (b + c)) = {expand or something idk}
        = ~(~bb + ~bc + b~c + ~cc) = {~aa = 0}
        = ~(~bc + b~c) } 
    =>
    = a(bc + ~b~c) + ~a~(bc + ~b~c)
    = a(b xor c) + ~a~(b xor c)
    = a xor (b xor c)
    = a xor b xor c

    carry_out = ~abc + ab +a~bc
    = c(b xor c) + ab

    This implementation follows the standard construction:
    - First half adder computes a xor b and a & b
    - Second half adder adds c_in
    - OR combines the carry signals
    """

    def __init__(self, name=None, num_inputs=3, num_outputs=2, input_names = None, output_names=None):
        input_names = ["a", "b", "c_in"]
        output_names = ["sum", "c_out"] 
        super().__init__(name, num_inputs, num_outputs, input_names, output_names)
        self.half_adder = HalfAdder()
        self._or = Or()

    def compute(self, inputs):
        """
        Compute the full-adder result.

        Args:
            inputs (list[bool] | int): Three input bits [a, b, c_in].

        Returns:
            list[bool]: [sum, carry_out].
        """
        a, b, c_in = self.input_handling(inputs, self.num_inputs)
        a_xor_b, a_and_b = self.half_adder.compute([a, b]) 
        sum, c_in_and_a_xor_b = self.half_adder.compute([a_xor_b, c_in])
        c_out = self._or.compute([c_in_and_a_xor_b, a_and_b])[0]
        return [sum, c_out]


class AddN(Chip):
    """
    n-bit ripple carry adder (RCA) which discards the final carry out bit.
    """
    def __init__(self, num_bits, name=None, input_names=None, output_names=None):
        self.num_bits = num_bits
        num_inputs = num_bits * 2
        num_outputs = num_bits

        input_names = input_names or [f"a_{i}" for i in range(num_bits)] + [f"b_{i}" for i in range(num_bits)]
        output_names = output_names or [f"s_{i}" for i in range(num_bits)]
        
        super().__init__(name, num_inputs, num_outputs, input_names, output_names)
        self.full_adder = FullAdder()
        self._or = Or()
        self._and = And()
        self.xor = Xor()

    def compute(self, inputs):
        """
        Compute the AddN result using ripple carry adder.

        Args:
            inputs (list[bool] | int): 2 n-bit numbers [n-bits]+[n-bits].

        Returns:
            list[bool]: [n-bit-sum].
        """
        inputs = self.input_handling(inputs, self.num_inputs)
        sum = []
        carry_in = 0
        a = inputs[:self.num_bits]
        b = inputs[self.num_bits:]
        for n in range(self.num_bits):
            sum_n, carry_in = self.full_adder.compute([a[n], b[n], carry_in])
            sum.append(sum_n)
        return sum
    
    def fast_compute(self, inputs):
        """
        Compute the AddN result using python's native logic.

        Args:
            inputs (list[bool] | int): 2 n-bit numbers [n-bits]+[n-bits].

        Returns:
            list[bool]: [n-bit-sum].
        """
        inputs = self.input_handling(inputs, self.num_inputs)
        a = inputs[:self.num_bits]
        b = inputs[self.num_bits:]
        
        a = bool_list_to_int(a)
        b = bool_list_to_int(b)
        python_sum = (a + b) % (1 << self.num_bits)
        return int_to_bool_list(python_sum, self.num_inputs)
    

class Inc16(Chip):
    """
    16-bit incrementer (++)
    """
    def __init__(self, name=None, num_inputs=16, num_outputs=16, input_names = None, output_names=None):
        input_names = input_names or [f"in_{i}" for i in range(num_inputs)]
        output_names = output_names or [f"s_{i}" for i in range(num_inputs)]
        super().__init__(name, num_inputs, num_outputs, input_names, output_names)
        self.add_16 = AddN(16)

    def compute(self, inputs):
        """
        Compute the incremented result using 16-bit adder.

        Args:
            inputs (list[bool] | int): 16-bit number.

        Returns:
            list[bool]: [16-bit-sum].
        """
        inputs = self.input_handling(inputs, self.num_inputs)
        return self.add_16.compute(inputs + [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])

    def fast_compute(self, inputs):
        """
        Compute the incremented result using python's native logic.

        Args:
            inputs (list[bool] | int): 16-bit number.

        Returns:
            list[bool]: [16-bit-sum].
        """
        return self.add_16.fast_compute(inputs + [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
    

class ALU(Chip):
    """
    Arithmetic Logic Unit (ALU).
    Negate or zero variables (x=0, x=!x, y=0, y=!y) and compute the following: x + y, x & y. 
    If output = 0: zr = 1. If output < 0 ng = 1
    """
    def __init__(self, num_bits=16, name=None, input_names=None, output_names=None):
        self.num_bits = num_bits
        num_inputs = 2 * num_bits + 6
        num_outputs = num_bits + 2
        input_names = input_names or [f"x{i}" for i in range(num_bits)] + [f"y{i}" for i in range(num_bits)] + ["zx", "nx", "zy", "ny", "f", "no"]
        output_names = output_names or [f"o_{i}" for i in range(num_inputs)]
        super().__init__(name, num_inputs, num_outputs, input_names, output_names)
        self.mux16 = MuxN(16)
        self.add16 = AddN(num_bits)
        self.and16 = AndN(16)
        self.not16 = NotN(16)
        self._or = Or()
        self._not = Not()

    def compute(self, inputs):
        """
        Compute the ALU's computation.

        Args:
            inputs (list[bool] | int): Two 16-bit binary numbers, zx, nx, zy, ny, f, no.

        Returns:
            list[bool]: [16-bit computation output] + [zr, ng].
        """
        inputs = self.input_handling(inputs, self.num_inputs)
        x = inputs[:self.num_bits]
        y = inputs[self.num_bits:self.num_bits * 2]
        zx, nx, zy, ny, f, no = inputs[self.num_bits * 2:]
        zx_x = self.mux16.compute([zx] + x + [0]*self.num_bits)
        not_x = self.not16.compute(zx_x)
        nx_x = self.mux16.compute([nx] + zx_x + not_x)

        zy_y = self.mux16.compute([zy] + y + [0]*self.num_bits)
        not_y = self.not16.compute(zy_y)
        ny_y = self.mux16.compute([ny] + zy_y + not_y)

        add16_computation = self.add16.compute(nx_x + ny_y)
        and16_computation = self.and16.compute(nx_x + ny_y)

        f_mux = self.mux16.compute([f] + and16_computation + add16_computation)
        not_out = self.not16.compute(f_mux)
        output = self.mux16.compute([no] + f_mux + not_out)

        zr_or = self.reduce_or(output)
        zr = self._not.compute(zr_or)

        ng = [output[15]]
        return output + zr + ng
                

    def fast_compute(self, inputs):
        """
        Compute the ALU's  computation using pythons's native logic.

        Args:
            inputs (list[bool] | int): Two 16-bit binary numbers, zx, nx, zy, ny, f, no.

        Returns:
            list[bool]: [16-bit computation output] + [zr, ng].
        """
        n = self.num_bits
        mask = (1 << n) - 1

        x = inputs[:n]
        y = inputs[n:2*n]
        zx, nx, zy, ny, f, no = inputs[2*n:]

        x = bool_list_to_int(x)
        y = bool_list_to_int(y)

        # Process x
        if zx:
            x = 0
        if nx:
            # mask      = ...0000001111111111111111
            # ~x        = ...111111xxxxxxxxxxxxxxxx
            # ~x & mask = ...000000xxxxxxxxxxxxxxxx
            x = (~x) & mask

        # Process y
        if zy:
            y = 0
        if ny:
            y = (~y) & mask

        # Function select    
        if f:
            out = (x + y) & mask
        else:
            out = x & y

        # Output negation
        if no:
            out = (~out) & mask # Throw away overflow with mask

        zr = int(out == 0)
        ng = (out >> (n - 1)) & 1

        return int_to_bool_list(out, bits=n) + [zr, ng]


    def reduce_or(self, bits):
        """
        Recursively ORs all bits using the ALU's _or gate.

        Args:
            bits (list[bool] | int): Bits to OR together, or an integer number.

        Returns:
            list[bool]: Single-element list containing the OR of all bits.
        """
        new_bits = []
        if len(bits) == 1:
            return bits
        for i in range(0, len(bits), 2):
            pair = bits[i:i+2]
            if len(pair) < 2:
                pair.append(False) # pad with 0 if odd
            new_bits.append(self._or.compute(pair)[0])
        return self.reduce_or(new_bits)



if __name__ == "__main__":
    """Example usecases"""
    
    half_adder = HalfAdder()
    inputs = [0,1]
    print(f" Half adder test. Inputs = {inputs}, Output: {half_adder.compute(inputs)}")

    N = 16
    a = 0b0100001111000100
    b = 0b0011110000111000

    a_bits = int_to_bool_list(a, N)
    b_bits = int_to_bool_list(b, N)
    add_n = AddN(N)

    python_sum = bin(bool_list_to_int(add_n.fast_compute(a_bits + b_bits)))
    my_sum = bin(bool_list_to_int(add_n.compute(a_bits + b_bits)))

    print(f"Python sum: {python_sum}, my programs calc: {my_sum}, are they the same? {python_sum == my_sum}")


    inc_16 = Inc16()
    print(f"Inc16 computation: {inc_16.compute(a)}")


    alu = ALU()
    zx=False
    nx=True 
    zy=False
    ny=True
    f=False
    no=True
    alu_computation = alu.compute(a_bits + b_bits + [zx, nx, zy, ny, f, no])
    fast_alu_computation = alu.fast_compute(a_bits + b_bits + [zx, nx, zy, ny, f, no])
    print(f"My ALU computation equal to pythons? {alu_computation == fast_alu_computation}")
    


    chips_I_want_to_test = [HalfAdder(), FullAdder(), AddN(2), ALU(4)]
    for chip in chips_I_want_to_test:
        chip.truth_table()
    