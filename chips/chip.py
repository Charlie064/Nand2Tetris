class Chip:
    def __init__(self, name = None, num_inputs = 0, num_outputs = 1, input_names = None, output_names = None):
        """Initialise a Chip instance.

        Args:
            name (str, optional): Name of the chip. Defaults to class name.
            num_inputs (int, optional): Number of input pins. Defaults to 0.
            num_outputs (int, optional): Number of output pins. Defaults to 1.
            input_names (list of str, optional): Names of input pins. Defaults to ['a', 'b', ...].
            output_names (list of str, optional): Names of output pins. Defaults to ['A', 'B', ...].
        """

        self.name = name or self.__class__.__name__
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs
        self.input_names = input_names or [chr(i) for i in range(97, 97 + self.num_inputs)]
        self.output_names = output_names or [chr(i) for i in range(65, 65 + self.num_outputs)]

    def truth_table(self, num_rows=None):
        """Print a truth table for the chip.

        Generates all possible input combinations (or a random subset when there are too many combinations) and prints
        the corresponding outputs by calling `compute()`.

        Args:
            num_rows (int, optional): Maximum number of rows to print. If None, all
                possible combinations are used (up to 32 rows). Defaults to None.

        Notes:
            Requires the `tabulate` module.
        """

        from tabulate import tabulate
        import random

        total_input_permutations = 2**len(self.input_names)
        if num_rows is None or num_rows > total_input_permutations:
            if total_input_permutations <= 32:
                num_rows = total_input_permutations
                compute_all = True
            else:
                num_rows = 8
                compute_all = False
        else:
            compute_all = False
        # Generate input patterns
        input_patterns = []
        for i in range(num_rows):
            if compute_all:
                val = i
            else:
                val = random.randint(0, total_input_permutations - 1)
            bits = format(val, f"0{self.num_inputs}b")                    # format each integer (0 -> total_permutations) in binary with appropriate zero padding
            input_patterns.append([b == "1" for b in bits])               # converts each "010" into [False, True, False]
        # Compute results
        rows = []
        for inputs in input_patterns:
            computation = self.compute(inputs)
            if not isinstance(computation, list):
                computation = [computation]
            row = [int(b) for b in inputs + computation]
            rows.append(row)

        headers = self.input_names + self.output_names
        print(f"Truth table for {self.name}:")
        print(f"{tabulate(rows, headers=headers, tablefmt="grid")}\n")

    def input_handling(self, inputs, num_inputs, input_message=None):
        """Formats inputs to list and handles incorrect inputs type and length.

        Args:
            inputs (list[bool] | int): 16-bit boolean list or integer.
            num_inputs (int): number of expected inputs.
            input_message (str, optional): specify what the inputs should be.

        Returns:
            list[bool]: correct boolean inputs list
        """
        if isinstance(inputs, int):
            inputs = int_to_bool_list(inputs)
        elif not isinstance(inputs, list):
            raise TypeError("Expected int or list")
        if len(inputs) != num_inputs:
            raise ValueError(f"Expected {num_inputs}-bit value {input_message}, got {len(inputs)} inputs")
        return inputs
    
            


def int_to_bool_list(value, bits=16):
    """Convert integer to list of boolean bits (LSB first).

    Args:
        value (int): Integer value to convert.
        bits (int, optional): Number of bits. Defaults to 16.

    Returns:
        list of bool: Boolean list representing the integer in binary.
    """
    # Move bits
    # & 1 == 1 checks if the new LSB is 1
    return [(((value >> i) & 1) == 1) for i in range(bits)]

def bool_list_to_int(bits):
    sum = 0
    for i, bit in enumerate(bits):
        if bit:
            sum += (1 << i)
    return sum


if __name__ == "__main__":
    pass