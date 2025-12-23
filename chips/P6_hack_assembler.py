import os


class Assembler:
    """Assembler for Hack assembly language.

    Translates .asm files to .hack machine code files.
    """

    def __init__(self):
        """Initialise instruction dictionaries."""

        # Variable symbols
        self.variable_symbols = {} 

        # Label symbols
        self.label_symbols = {}
        self.largest_symb_num = 16
        # Pre-defined symbols:
        reg_symbols = {f"R{i}":f"{i}" for i in range(16)}
        other_symbols = {
            "SP": "0",
            "LCL": "1",
            "ARG": "2",
            "THIS": "3",
            "THAT": "4",
            "SCREEN": "16384",
            "KBD": "24576"
        }
        self.predef_symbols = reg_symbols | other_symbols

        # Token symbols:
        self.dest_dict = {
            "null": "000",
            "M": "001",
            "D": "010",
            "MD": "011",
            "A": "100",
            "AM": "101",
            "AD": "110",
            "AMD": "111"
        }

        self.comp_dict = {
            "0": "0101010",
            "1": "0111111",
            "-1": "0111010",
            "D": "0001100",
            "A": "0110000",
            "M": "1110000",
            "!D": "0001101",
            "!A": "0110001",
            "!M": "1110001",
            "-D": "0001111",
            "-A": "0110011",
            "-M": "1110011",
            "D+1": "0011111",
            "A+1": "0110111",
            "M+1": "1110111",
            "D-1": "0001110",
            "A-1": "0110010",
            "M-1": "1110010",
            "D+A": "0000010",
            "D+M": "1000010",
            "D-A": "0010011",
            "D-M": "1010011",
            "A-D": "0000111",
            "M-D": "1000111",
            "D&A": "0000000",
            "D&M": "1000000",
            "D|A": "0010101",
            "D|M": "1010101"
        }

        self.jump_dict = {
            "null": "000",
            "JGT": "001",
            "JEQ": "010",
            "JGE": "011",
            "JLT": "100",
            "JNE": "101",
            "JLE": "110",
            "JMP": "111"
        }

       
    def assemble(self, file_name = "test"):
        """
        Reads an .asm file, translates it to Hack machine code,
        and writes the resulting .hack file.

        Args:
            file_name (str): Base filename (without extension)
        """

        script_dir = os.path.dirname(__file__)
        input_path = os.path.join(script_dir, (file_name + ".asm"))
        output_path = os.path.join(script_dir, (file_name + ".hack"))

        assembly_lines = self.first_parse(input_path)
        assembly_lines = self.second_parse(assembly_lines)
        self.write_file(output_path, assembly_lines)

       
    def first_parse(self, input_path):
        """
        First assembly pass.
        Removes comments and labels, and records label ROM addresses.

        Args:
            input_path (str): Path to the input .asm file

        Returns:
            list[tuple[str, int]]:
                List of (instruction, original_source_line_number)
        """

        assembly_lines = []
        rom_address = 0

        with open(input_path, "r") as input_file:

            for source_line_number, line in enumerate(input_file, start=1):
                    
                line = line.split("//", 1)[0].strip()
                
                if not line:
                    continue

                if line.startswith("(") and line.endswith(")"):
                    label = line[1:-1]
                    if label in self.label_symbols:
                        print(f"Duplicate label on line {source_line_number}: '{label}'")
                    else:
                        self.label_symbols[label] = rom_address
                    continue
                
                # Validate instruction before counting it
                if self.is_valid_a_instruction(line) or self.is_valid_c_instruction(line):
                    assembly_lines.append((line, source_line_number))
                    rom_address += 1 
                else:
                    print(f"Ignoring invalid instruction on line {source_line_number}: {line}")

            return assembly_lines
        

    def second_parse(self, assembly_lines):
        """
        Second assembly pass.
        Translates A and C-instructions into 16-bit binary code.

        Args:
            assembly_lines (list[tuple[str, int]]):
                Instructions produced by the first pass

        Returns:
            list[str]:
                List of 16-bit binary instruction strings
        """
        binary_lines = []

        for line, source_line_number in assembly_lines: 
            if line.startswith("@"):
                binary = self.parse_a_instruction(line, source_line_number)
            else:
                binary = self.parse_c_instruction(line, source_line_number)
                
            if binary:
                binary_lines.append(binary)

        return binary_lines


    def parse_a_instruction(self, line, source_line_number):
        """
        Translates an A-instruction into 16-bit binary.

        Resolves constants, predefined symbols, labels,
        and allocates new variables starting at RAM address 16.

        Args:
            line (str): A-instruction (e.g. "@5", "@LOOP")
            source_line_number (int): Source line number

        Returns:
            str | None:
                16-bit binary string, or None if invalid
        """

        token = line[1:]

        if not token.isdigit():
            if token in self.predef_symbols:
                token = self.predef_symbols[token]
            elif token in self.label_symbols:
                token = self.label_symbols[token]
            elif token in self.variable_symbols:
                token = self.variable_symbols[token]
            else: 
                self.variable_symbols[token] = self.largest_symb_num
                self.largest_symb_num += 1
                token = self.variable_symbols[token]
            
        try:
            address_symbol = int(token)

        except ValueError:
            print(f"Invalid A-instruction on line {source_line_number}: {line} (invalid number)")
            return None
        
        if not (0 <= address_symbol <= 2**15 - 1):
            print(f"Invalid A-instruction on line {source_line_number}: {token} (out of range) ")
            return None
        
        return f"{address_symbol:016b}"


    def parse_c_instruction(self, line, source_line_number):
        """
        Translates a C-instruction into 16-bit binary.

        Splits the instruction into dest, comp, and jump fields,
        then encodes each field using lookup tables.

        Args:
            line (str): C-instruction (dest=comp;jump)
            source_line_number (int): Source line number

        Returns:
            str | None:
                16-bit binary string, or None if invalid
        """
        dest, comp, jump = self.split_c_instruction(line)
        try:
            comp_bits = self.comp_dict[comp]
            dest_bits = self.dest_dict[dest]
            jump_bits = self.jump_dict[jump]
            
        except KeyError as e:
            print(f"Invalid C-instruction on line {source_line_number}: {line} (unknown {e})")
            return None

        return "111" + comp_bits + dest_bits + jump_bits

    def is_valid_a_instruction(self, line):
        """
        Checks whether a line has the basic structure of an A-instruction.

        Args:
            line (str): Source line

        Returns:
            bool: True if line starts with '@' and has content with allowed symbols
        """
        if not line.startswith("@") or len(line) < 2:
            return False
        
        token = line[1:]

        if token.isdigit():
            return True
        
        allowed_first_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabdcefghijklmnopqrstuvwxyz_.$"
        allowed_chars = allowed_first_chars + "0123456789"
        if token[0] not in allowed_first_chars:
            return False
        for char in token[1:]:
            if char not in allowed_chars:
                return False

        return True
    

    def is_valid_c_instruction(self, line):
        """
        Checks whether a line is a valid C-instruction.

        Validity is determined by verifying that dest, comp,
        and jump fields exist in their respective lookup tables.

        Args:
            line (str): Source line

        Returns:
            bool: True if instruction is valid
        """

        dest, comp, jump = self.split_c_instruction(line)
        if dest not in self.dest_dict:
            return False
        if comp not in self.comp_dict:
            return False
        if jump not in self.jump_dict:
            return False
        return True
    

    def split_c_instruction(self, line):
        """
        Splits a C-instruction into dest, comp, and jump fields.

        Missing fields are replaced with 'null'.

        Args:
            line (str): C-instruction string

        Returns:
            tuple[str, str, str]:
                (dest, comp, jump)
        """
        if ";" in line:
            rest, jump = line.split(";", 1)
        else:
            rest, jump = line, "null"

        if "=" in rest:
            dest, comp = rest.split("=", 1)
        else:
            dest, comp = "null", rest

        dest = dest.strip()
        comp = comp.strip()
        jump = jump.strip()

        return dest, comp, jump


    def write_file(self, output_path, binary_lines):
        """
        Writes translated machine code to a .hack file.

        Args:
            output_path (str): Path to output file
            binary_lines (list[str]): 16-bit binary instructions
        """
        with open(output_path, "w") as output_file:     
            for line in binary_lines:
                output_file.write(f"{line}\n")



if __name__ == "__main__":
    assembler = Assembler()
    assembler.assemble()