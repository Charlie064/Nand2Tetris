class Chip:
    def __init__(self, name = None, num_inputs = 0, num_outputs = 1, input_names = None, output_names = None):
        self.name = name or self.__class__.__name__
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs
        self.input_names = input_names or [chr(i) for i in range(97, 97 + self.num_inputs)]
        self.output_names = output_names or [chr(i) for i in range(65, 65 + self.num_inputs)]

    def truth_table(self):
        from tabulate import tabulate
        num_input_permutations = 2**len(self.input_names)
        input_permuations_bool = []
        input_permutations_bin = []
        for i in range(num_input_permutations):
            bits = format(i, f"0{self.num_inputs}b")                # format each integer (0 -> total_permutations) in binary with appropriate zero padding
            input_permuations_bool.append([b == "1" for b in bits])     # converts each "010" into [False, True, False]
            input_permutations_bin.append(bits)
        #print(f"input permuatations bin: {input_permutations_bin}")
        #print(f"input permuatations bool: {input_permuations_bool}") 
        a = []
        for inputs in input_permuations_bool:
            row = [int(b) for b in inputs]
            computation = self.compute(*inputs)
            if isinstance(computation, list):
                for output in computation:
                    row.append(int(output))
            else:
                row.append(int(computation))
            a.append(row)


        # old, didn't work on Dmux:a = [[int(b) for b in inputs] + [int(self.compute(*inputs))] for inputs in input_permuations_bool]
        headers = self.input_names + self.output_names
        print(f"Truth table for {self.name}:")
        print(f"{tabulate(a, headers=headers, tablefmt="grid")}\n")
