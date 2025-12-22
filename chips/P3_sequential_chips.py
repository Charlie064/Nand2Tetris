from P1_multi_way_logic_gates import Mux, Mux8Way16, DMux8Way, DMux4Way, Mux4Way16
from P1_16bit_logic_gates import MuxN
from P2_Adding import Inc16
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
    

    def set_input(self, D=None):
        """
        Set the D input value.

        Args:
            D (bool | int): Input value to be latched on the next rising clock edge.
        """
        if D is not None:
            self.D = bool(D)


    def get_output(self):
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
        input_names = input_names or ["in", "load"]
        output_names = output_names or ["out"]

        super().__init__(name, num_inputs, num_outputs, input_names, output_names)
        self.mux = Mux()
        self.dff = DFF()
        self.in_val_D = False
        self.load = False


    def set_input(self, inputs=None):
        """
        Set input and load signal.

        Args:
            inputs (list[bool]): [in, load]
        """
        if inputs is not None:
            self.in_val_D, self.load = self.input_handling(inputs, 2, "1 input, 1 load")
        current_Q, _ = self.dff.get_output()
        self.in_val_D = self.mux.compute([self.load, current_Q, self.in_val_D])[0]
        self.dff.set_input(self.in_val_D)


    def get_output(self):
        """
        Return current stored bit.

        Returns:
            list[bool]: [out]
        """
        Q, _ = self.dff.get_output()
        return [Q]
    

    def on_clock(self, clk):
        """
        Forward clock to internal DFF.

        Args:
            clk (bool | int): Current clock level.
        """
        self.set_input()
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


    def set_input(self, inputs=None):
        """
        Set inputs and load signal.

        Args:
            inputs (list[bool]): [in_0, in_1, ..., in_{N-1}, load]
        """
        if inputs is not None:
            inputs = self.input_handling(inputs, self.num_inputs, "(N-inputs, 1 load)")
            self.in_vals = inputs[:-1]
            self.load = inputs[-1]

        for i in range(self.num_bits):
            self.bits[i].set_input([self.in_vals[i], self.load])


    def get_output(self):
        """
        Return current stored value of the register.

        Returns:
            list[bool]: N-bit output
        """
        return [bit.get_output()[0] for bit in self.bits]
    

    def on_clock(self, clk):
        """
        Forward clock to internal bits.

        Args:
            clk (bool | int): Current clock level.
        """
        self.set_input()
        for bit in self.bits:
            bit.on_clock(clk)



class RAM8(Chip):
    """
    8-word RAM with 16-bit words.

    Consists of 8 registers, each storing a 16-bit value.
    A 3-bit address selects which register is accessed.

    - Reads are combinational (no clock required).
    - Writes occur on the next rising clock edge when self.load is asserted.
    """
    def __init__(self, name=None, num_inputs=16 + 3 + 1, num_outputs=16, input_names = None, output_names=None):
        input_names = input_names or [f"in_{i}" for i in range(16)] + ["adrs_0", "adrs_1", "adrs_2", "load"]
        output_names = output_names or [f"out_{i}" for i in range(16)]

        super().__init__(name, num_inputs, num_outputs, input_names, output_names)
        self.dmux8way = DMux8Way()
        self.mux8way16 = Mux8Way16()
        self.registers = [RegisterN(16, name=f"register{i}") for i in range(8)]
        self.in_val = [False]*16
        self.address = [False]*3
        self.load = False

    
    def __getitem__(self, address):
        """
        Used for reading using indexing: value = RAM[address]
        This performs a slow combinational read and updates self.address.

        Args:
            address (list[bool]): 3-bit address

        Returns:
            list[bool]: 16-bit value stored at the addressed register
        """
         
        address = self.input_handling(address, 3)
        return self.get_output(address)
    

    def __setitem__(self, address, value):
        """
        Used for writing using indexing: RAM[address] = value
        This performs a slow combinational write and updates self.address and self.in_val.

        NOTE:
        - This does NOT force a write by itself.
        - Whether a write occurs depends on the current value of `load`
          and the next clock edge.

        Args:
            address (list[bool]): 3-bit address
            value (list[bool]): 16-bit input value
        """
        self.address = self.input_handling(address, 3, "3-bit address")
        self.in_val = self.input_handling(value, 16, "16-bit input")
        self.set_input()


    def get_output(self, address):
        """
        Computes the current RAM output.
        -Reads all registers combinationally
        -Uses Mux8Way16 to select the output of the addressed register

        This method does not modify state and does not require a clock.

        Returns:
            list[bool]: 16-bit output of the selected register
        """
        reg_outputs = []
        for reg in self.registers:
            reg_outputs.extend(reg.get_output())
        return self.mux8way16.compute(address + reg_outputs)
    
    
    def set_input(self, inputs=None):
        """
        Updates the input of the RAM.
        -Uses previous inputs (in_vals, address, load) if inputs = None
        -Updates inputs (self.in_vals, self.address, self.load) if inputs is provided.
        Uses slow combinational hardware behaviour.

        Args:
            inputs (list[bool]): 16-bit value, 3-bit address and 1-bit load
        """
        if inputs is not None:
            inputs = self.input_handling(inputs, self.num_inputs, "(16 inputs, 3 address, 1 load)")
            self.in_val = inputs[0:16]
            self.address = inputs[16:19]
            self.load = inputs[19]
            
        dmux_outputs = self.dmux8way.compute(self.address + [self.load])
        for i in range(8):
            self.registers[i].set_input(self.in_val + [dmux_outputs[i]])
    

    def on_clock(self, clk):
        """
        Propagate the clock signal to all internal registers.

        On a rising clock edge:
        - Only the register whose load signal is asserted
          will latch the input value
        - All other registers retain their previous state

        Args:
            clk (bool | int): Current clock level
        """
        self.set_input()
        for reg in self.registers:
            reg.on_clock(clk)
    


class RAM64(Chip):
    """
    64-word RAM with 16-bit words.

    Consists of 64 registers, each storing a 16-bit value.
    A 6-bit address selects which register is accessed.

    - Reads are combinational (no clock required).
    - Writes occur on the next rising clock edge when self.load is asserted.
    """
    def __init__(self, name=None, num_inputs=16 + 6 + 1, num_outputs=16, input_names = None, output_names=None):
        input_names = input_names or [f"in_{i}" for i in range(16)] + [f"adrs_{i}" for i in range(6)] + ["load"]
        output_names = output_names or [f"out_{i}" for i in range(16)]

        super().__init__(name, num_inputs, num_outputs, input_names, output_names)
        self.dmux8way = DMux8Way()
        self.mux8way16 = Mux8Way16()
        self.ram8blocks = [RAM8(name=f"RAM8_{i}") for i in range(8)]

        self.in_val = [False]*16
        self.address = [False]*6
        self.load = False

    
    def __getitem__(self, address):
        """
        Used for reading using indexing: value = RAM[address]
        This performs a slow combinational read and updates self.address.

        Args:
            address (list[bool]): 6-bit address

        Returns:
            list[bool]: 16-bit value stored at the addressed register
        """
        address = self.input_handling(address, 6)
        return self.get_output(address)
    

    def __setitem__(self, address, value):
        """
        Used for writing using indexing: RAM[address] = value
        This performs a slow combinational write and updates self.address and self.in_val.

        NOTE:
        - This does NOT force a write by itself.
        - Whether a write occurs depends on the current value of `load`
          and the next clock edge.

        Args:
            address (list[bool]): 6-bit address
            value (list[bool]): 16-bit input value
        """
        self.address = self.input_handling(address, 6, "6-bit address")
        self.in_val = self.input_handling(value, 16, "16-bit input")
        self.set_input()


    def get_output(self, address):
        """
        Computes the current RAM output.
        -Reads all registers combinationally
        -Uses Mux8Way16 to select the output of the addressed register

        This method does not modify state and does not require a clock.

        Returns:
            list[bool]: 16-bit output of the selected register
        """
        high_addr = address[3:6]
        low_addr = address[0:3]

        ram_output = []
        for ram_block in self.ram8blocks:
            ram_output.extend(ram_block.get_output(low_addr))
        return self.mux8way16.compute(high_addr + ram_output)
    
    
    def set_input(self, inputs=None):
        """
        Updates the input of the RAM.
        -Uses previous inputs (in_vals, address, load) if inputs = None
        -Updates inputs (self.in_vals, self.address, self.load) if inputs is provided.
        Uses slow combinational hardware behaviour.

        Args:
            inputs (list[bool]): 16-bit value, 6-bit address and 1-bit load
        """
        if inputs is not None:
            inputs = self.input_handling(inputs, self.num_inputs, "(16 inputs, 6 address, 1 load)")
            self.in_val = inputs[0:16]
            self.address = inputs[16:22]
            self.load = inputs[22]

        high_addr = self.address[3:6]
        low_addr  = self.address[0:3]

        dmux_outputs = self.dmux8way.compute(high_addr + [self.load])

        for i in range(8):
            self.ram8blocks[i].set_input(self.in_val + low_addr + [dmux_outputs[i]])

    def on_clock(self, clk):
        """
        Propagate the clock signal to all internal registers.

        On a rising clock edge:
        - Only the register whose load signal is asserted
          will latch the input value
        - All other registers retain their previous state

        Args:
            clk (bool | int): Current clock level
        """
        self.set_input()
        for ram_block in self.ram8blocks:
            ram_block.on_clock(clk)



class RAM512(Chip):
    """
    512-word RAM with 16-bit words.

    Consists of 8 registers, each storing a 16-bit value.
    A 9-bit address selects which register is accessed.

    - Reads are combinational (no clock required).
    - Writes occur on the next rising clock edge when self.load is asserted.
    """
    def __init__(self, name=None, num_inputs=16 + 9 + 1, num_outputs=16, input_names = None, output_names=None):
        input_names = input_names or [f"in_{i}" for i in range(16)] + [f"adrs_{i}" for i in range(9)] + ["load"]
        output_names = output_names or [f"out_{i}" for i in range(16)]

        super().__init__(name, num_inputs, num_outputs, input_names, output_names)
        self.dmux8way = DMux8Way()
        self.mux8way16 = Mux8Way16()
        self.ram64blocks = [RAM64(name=f"RAM64_{i}") for i in range(8)]

        self.in_val = [False]*16
        self.address = [False]*9
        self.load = False

    
    def __getitem__(self, address):
        """
        Used for reading using indexing: value = RAM[address]
        This performs a slow combinational read and updates self.address.

        Args:
            address (list[bool]): 9-bit address

        Returns:
            list[bool]: 16-bit value stored at the addressed register
        """
        address = self.input_handling(address, 9)
        return self.get_output(address)
    

    def __setitem__(self, address, value):
        """
        Used for writing using indexing: RAM[address] = value
        This performs a slow combinational write and updates self.address and self.in_val.

        NOTE:
        - This does NOT force a write by itself.
        - Whether a write occurs depends on the current value of `load`
          and the next clock edge.

        Args:
            address (list[bool]): 9-bit address
            value (list[bool]): 16-bit input value
        """
        self.address = self.input_handling(address, 9, "9-bit address")
        self.in_val = self.input_handling(value, 16, "16-bit input")
        self.set_input()


    def get_output(self, address):
        """
        Computes the current RAM output.
        -Reads all registers combinationally
        -Uses Mux8Way16 to select the output of the addressed register

        This method does not modify state and does not require a clock.

        Returns:
            list[bool]: 16-bit output of the selected register
        """
        high_addr = address[6:9]
        low_addr = address[0:6]

        ram_output = []
        for ram_block in self.ram64blocks:
            ram_output.extend(ram_block.get_output(low_addr))
        return self.mux8way16.compute(high_addr + ram_output)
    
    
    def set_input(self, inputs=None):
        """
        Updates the input of the RAM.
        -Uses previous inputs (in_vals, address, load) if inputs = None
        -Updates inputs (self.in_vals, self.address, self.load) if inputs is provided.
        Uses slow combinational hardware behaviour.

        Args:
            inputs (list[bool]): 16-bit value, 9-bit address and 1-bit load
        """
        if inputs is not None:
            inputs = self.input_handling(inputs, self.num_inputs, "(16 inputs, 9 address, 1 load)")
            self.in_val = inputs[0:16]
            self.address = inputs[16:25]
            self.load = inputs[25]

        high_addr = self.address[6:9]
        low_addr  = self.address[0:6]

        dmux_outputs = self.dmux8way.compute(high_addr + [self.load])

        for i in range(8):
            self.ram64blocks[i].set_input(self.in_val + low_addr + [dmux_outputs[i]])
    

    def on_clock(self, clk):
        """
        Propagate the clock signal to all internal registers.

        On a rising clock edge:
        - Only the register whose load signal is asserted
          will latch the input value
        - All other registers retain their previous state

        Args:
            clk (bool | int): Current clock level
        """
        self.set_input()
        for ram_block in self.ram64blocks:
            ram_block.on_clock(clk)



class RAM4K(Chip):
    """
    4096-word RAM with 16-bit words.

    Consists of 8 registers, each storing a 16-bit value.
    A 12-bit address selects which register is accessed.

    - Reads are combinational (no clock required).
    - Writes occur on the next rising clock edge when self.load is asserted.
    """
    def __init__(self, name=None, num_inputs=16 + 12 + 1, num_outputs=16, input_names = None, output_names=None):
        input_names = input_names or [f"in_{i}" for i in range(16)] + [f"adrs_{i}" for i in range(12)] + ["load"]
        output_names = output_names or [f"out_{i}" for i in range(16)]

        super().__init__(name, num_inputs, num_outputs, input_names, output_names)
        self.dmux8way = DMux8Way()
        self.mux8way16 = Mux8Way16()
        self.ram512blocks = [RAM512(name=f"RAM512_{i}") for i in range(8)]

        self.in_val = [False]*16
        self.address = [False]*12
        self.load = False

    
    def __getitem__(self, address):
        """
        Used for reading using indexing: value = RAM[address]
        This performs a slow combinational read and updates self.address.

        Args:
            address (list[bool]): 12-bit address

        Returns:
            list[bool]: 16-bit value stored at the addressed register
        """
        address = self.input_handling(address, 12)
        return self.get_output(address)
    

    def __setitem__(self, address, value):
        """
        Used for writing using indexing: RAM[address] = value
        This performs a slow combinational write and updates self.address and self.in_val.

        NOTE:
        - This does NOT force a write by itself.
        - Whether a write occurs depends on the current value of `load`
          and the next clock edge.

        Args:
            address (list[bool]): 12-bit address
            value (list[bool]): 16-bit input value
        """
        self.address = self.input_handling(address, 12, "12-bit address")
        self.in_val = self.input_handling(value, 16, "16-bit input")
        self.set_input()


    def get_output(self, address):
        """
        Computes the current RAM output.
        -Reads all registers combinationally
        -Uses Mux8Way16 to select the output of the addressed register

        This method does not modify state and does not require a clock.

        Returns:
            list[bool]: 16-bit output of the selected register
        """
        high_addr = address[9:12]
        low_addr = address[0:9]

        ram_output = []
        for ram_block in self.ram512blocks:
            ram_output.extend(ram_block.get_output(low_addr))
        return self.mux8way16.compute(high_addr + ram_output)
    
    
    def set_input(self, inputs=None):
        """
        Updates the input of the RAM.
        -Uses previous inputs (in_vals, address, load) if inputs = None
        -Updates inputs (self.in_vals, self.address, self.load) if inputs is provided.
        Uses slow combinational hardware behaviour.

        Args:
            inputs (list[bool]): 16-bit value, 12-bit address and 1-bit load
        """
        if inputs is not None:
            inputs = self.input_handling(inputs, self.num_inputs, "(16 inputs, 12 address, 1 load)")
            self.in_val = inputs[0:16]
            self.address = inputs[16:28]
            self.load = inputs[28]

        high_addr = self.address[9:12]
        low_addr  = self.address[0:9]

        dmux_outputs = self.dmux8way.compute(high_addr + [self.load])

        for i in range(8):
            self.ram512blocks[i].set_input(self.in_val + low_addr + [dmux_outputs[i]])
    

    def on_clock(self, clk):
        """
        Propagate the clock signal to all internal registers.

        On a rising clock edge:
        - Only the register whose load signal is asserted
          will latch the input value
        - All other registers retain their previous state

        Args:
            clk (bool | int): Current clock level
        """
        self.set_input()
        for ram_block in self.ram512blocks:
            ram_block.on_clock(clk)


class RAM16K(Chip):
    """
    16384-word RAM with 16-bit words.

    Consists of 8 registers, each storing a 16-bit value.
    A 14-bit address selects which register is accessed.

    - Reads are combinational (no clock required).
    - Writes occur on the next rising clock edge when self.load is asserted.
    """
    def __init__(self, name=None, num_inputs=16 + 14 + 1, num_outputs=16, input_names = None, output_names=None):
        input_names = input_names or [f"in_{i}" for i in range(16)] + [f"adrs_{i}" for i in range(14)] + ["load"]
        output_names = output_names or [f"out_{i}" for i in range(16)]

        super().__init__(name, num_inputs, num_outputs, input_names, output_names)
        self.dmux4way = DMux4Way()
        self.mux4way16 = Mux4Way16()
        self.ram4kblocks = [RAM4K(name=f"RAM4K_{i}") for i in range(4)]

        self.in_val = [False]*16
        self.address = [False]*14
        self.load = False

    
    def __getitem__(self, address):
        """
        Used for reading using indexing: value = RAM[address]
        This performs a slow combinational read and updates self.address.

        Args:
            address (list[bool]): 14-bit address

        Returns:
            list[bool]: 16-bit value stored at the addressed register
        """
        address = self.input_handling(address, 14)
        return self.get_output(address)
    

    def __setitem__(self, address, value):
        """
        Used for writing using indexing: RAM[address] = value
        This performs a slow combinational write and updates self.address and self.in_val.

        NOTE:
        - This does NOT force a write by itself.
        - Whether a write occurs depends on the current value of `load`
          and the next clock edge.

        Args:
            address (list[bool]): 14-bit address
            value (list[bool]): 16-bit input value
        """
        self.address = self.input_handling(address, 14, "14-bit address")
        self.in_val = self.input_handling(value, 16, "16-bit input")
        self.set_input()


    def get_output(self, address):
        """
        Computes the current RAM output.
        -Reads all registers combinationally
        -Uses Mux8Way16 to select the output of the addressed register

        This method does not modify state and does not require a clock.

        Returns:
            list[bool]: 16-bit output of the selected register
        """
        high_addr = address[12:14]
        low_addr = address[0:12]

        ram_output = []
        for ram_block in self.ram4kblocks:
            ram_output.extend(ram_block.get_output(low_addr))
        return self.mux4way16.compute(high_addr + ram_output)
    
    
    def set_input(self, inputs=None):
        """
        Updates the input of the RAM.
        -Uses previous inputs (in_vals, address, load) if inputs = None
        -Updates inputs (self.in_vals, self.address, self.load) if inputs is provided.
        Uses slow combinational hardware behaviour.

        Args:
            inputs (list[bool]): 16-bit value, 6-bit address and 1-bit load
        """
        if inputs is not None:
            inputs = self.input_handling(inputs, self.num_inputs, "(16 inputs, 14 address, 1 load)")
            self.in_val = inputs[0:16]
            self.address = inputs[16:30]
            self.load = inputs[30]

        high_addr = self.address[12:14]
        low_addr  = self.address[0:12]

        dmux_outputs = self.dmux4way.compute(high_addr + [self.load])

        for i in range(4):
            self.ram4kblocks[i].set_input(self.in_val + low_addr + [dmux_outputs[i]])
    

    def on_clock(self, clk):
        """
        Propagate the clock signal to all internal registers.

        On a rising clock edge:
        - Only the register whose load signal is asserted
          will latch the input value
        - All other registers retain their previous state

        Args:
            clk (bool | int): Current clock level
        """
        self.set_input()
        for ram_block in self.ram4kblocks:
            ram_block.on_clock(clk)



class PC(Chip):
    """
    16-bit Program Counter.

    Stores the address of the next instruction to execute.

    The PC supports three control signals:
    - load  : load an external 16-bit value
    - inc   : increment the current value by 1
    - reset : reset the counter to 0

    Priority (highest to lowest):
    1. reset
    2. load
    3. inc
    4. hold current value

    - Output is always the current stored value.
    - State updates occur only on rising clock edges.
    """

    def __init__(self, name=None, num_inputs=16 + 3, num_outputs=16, input_names = None, output_names=None):
        input_names = input_names or [f"in_{i}" for i in range(16)] + ["load", "inc", "reset"]
        output_names = output_names or [f"out_{i}" for i in range(16)]

        super().__init__(name, num_inputs, num_outputs, input_names, output_names)
        self.mux16 = MuxN(16)
        self.increment = Inc16()
        self.reg16 = RegisterN(16)

        self.in_val = [False]*16
        self.load = False
        self.inc = False
        self.reset = False


    def get_output(self):
        """
        Read and return the current value of the program counter without modifying states.

        Returns:
            list[bool]: 16-bit current PC value
        """
        return self.reg16.get_output()
    
    
    def set_input(self, inputs=None):
        """
        Update the input and control signals of the PC.

        If inputs is None, the previously stored control inputs (load/inc/reset) are reused.

        The next register input is computed combinationally according
        to the following priority:

        if reset[t]==1:
            out[t+1] = 0
        elif (load[t]==1)
            out[t+1] = in[t]
        elif (inc[t]==1):
            out[t+1] = out[t] + 1
        else:
            out[t+1] = out[t]

        Args:
            inputs (list[bool]): 16-bit input value followed by
                                 [load, inc, reset]
        """
        if inputs is not None:
            inputs = self.input_handling(inputs, self.num_inputs, "(16 inputs, 1 load, 1 inc, 1 reset)")
            self.in_val = inputs[0:16]
            self.load = inputs[16]
            self.inc = inputs[17]
            self.reset = inputs[18]

        output = self.get_output()
        out_inc = self.increment.compute(output)

        inc_mux_out = self.mux16.compute([self.inc]  + output + out_inc)
        load_mux_out = self.mux16.compute([self.load] + inc_mux_out + self.in_val)
        reg_input = self.mux16.compute([self.reset] + load_mux_out + [0]*16)

        self.reg16.set_input(reg_input + [True])
    

    def on_clock(self, clk):
        """
        Propagate the clock signal to the internal register.

        Args:
            clk (bool | int): Current clock level
        """
        self.set_input()
        self.reg16.on_clock(clk)



if __name__ == "__main__":
    """
    RAM demo showing:
    1. Combinational reads (no clock)
    2. Writes that only take effect on clock edges
    3. Addressed access behaving like a list
    """

    ram_dict = {
  "ram8": [RAM8(), 3],
  "ram64": [RAM64(), 6],
  "ram512": [RAM512(), 9],
  "ram4k": [RAM4K(), 12],
  "ram16k": [RAM16K(), 14]
}
    
    # NOTE: Change the key to test different RAM sizes.
    ram, address_size = ram_dict["ram8"]


    clock = Clock()
    clock.subscribe([ram])

    # Setup values

    value = 0b111111111111110
    value = int_to_bool_list(value)

    address = [False, False, True, False, False, True, False, False, True, False, False, True, True, True]
    address = address[:address_size]
    address_num = bool_list_to_int(address)
    no_load = [False]
    load = [True]

    print("=== RAM DEMO ===\n")

    print("Initial RAM state (all zeros):")
    print(f"RAM[{address_num}] = {ram[address]}\n")

    # Write attempt WITHOUT load

    print("Attempt write without load (should NOT change RAM):")

    ram.set_input(value + address + no_load)
    print("Inputs set (value, address, load=False)")
    print(f"Before clock tick, RAM[{address_num}] = {ram[address]}")

    clock.tick()
    print(f"After clock tick, RAM[{address_num}] = {ram[address]}\n")

    # Write WITH load enabled

    print("Write with load enabled:")

    ram.set_input(value + address + load)
    print("Inputs set (value, address, load=True)")
    print(f"Before clock tick, RAM[{address_num}] = {ram[address]}")

    clock.tick()
    print(f"After clock tick, RAM[{address_num}] = {ram[address]}\n")

    # Other addresses are unaffected

    print("Verify other addresses are unchanged:")
    for i in range(2**(len(address))):
        addr = int_to_bool_list(i, bits=address_size)
        print(f"RAM[{i}] = {ram[addr]}")



    """
    PC demo showing:
    1. Do nothing (PC holds value)
    2. Load an external 16-bit value
    3. Reset the PC to 0 (reset has highest priority)
    4. Increment the PC multiple times
    """

    pc = PC()
    clock_pc = Clock()

    clock_pc.subscribe([pc])
    input_value = 0b1111111111111111
    input_value = int_to_bool_list(input_value, 16)

    print("=== PC DEMO ===\n")

    # 1. Do nothing test.

    print(f"Initial PC value (zero): {pc.get_output()}")

    # 2. Load test.
    load = True
    increment = False
    reset = False
    
    pc.set_input(input_value + [load, increment, reset])
    clock_pc.tick()
    print(f"PC after load: {pc.get_output()}")

    #3. Reset test (takes priority over load/inc)
    load = True
    increment = False
    reset = True
    
    pc.set_input(input_value + [load, increment, reset])
    clock_pc.tick()
    print(f"PC after reset: {pc.get_output()}")

    # 4. Increment test (only works if load and reset are 0)
    load = False
    increment = True
    reset = False
    
    pc.set_input(input_value + [load, increment, reset])

    n = 15
    for _ in range(n):
        clock_pc.tick()
    print(f"PC after {n} increments: {pc.get_output()}")