"""
CPU functionality.

skipped so far:
CALL
INT
IRET
JEQ
JGE
JGT
JLE
JMP
JNE
POP
PUSH
RET


Maybe I can do this?
ST


come back to these
PRA 
SHL
SHR
SUB
XOR
"""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.mar = 0
        self.mdr = 0
        self.running = True

        # set comparison flags default to 0 (last 3 bits are L, G, E)
        self.FL = 0b00000000

        # alu operation table
        self.alutable = {}
        self.alutable[0b0] = "ADD"
        self.alutable[0b10] = "MUL"
        self.alutable[0b0111] = "CMP"
        self.alutable[0b110] = "DEC"
        self.alutable[0b101] = "INC"
        self.alutable[0b11] = "DIV"
        self.alutable[0b100] = "MOD"
        self.alutable[0b1000] = "AND"
        self.alutable[0b1010] = "OR"
        self.alutable[0b1001] = "NOT"

        # non-alu instruction definitions
        self.branchtable = {}
        self.branchtable[0b1] = self.HLT
        self.branchtable[0b10] = self.LDI
        self.branchtable[0b11] = self.LD
        self.branchtable[0b111] = self.PRN

    def ram_read(self):
        return self.reg[self.mar]

    def ram_write(self):
        self.reg[self.mar] = self.mdr

    def load(self, program):
        """Load a program into memory."""
        address = 0
        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def alu(self, op, reg_a=None, reg_b=None):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "DEC":
            self.reg[reg_a] -= 1
        elif op == "INC":
            self.reg[reg_a] += 1
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]
        elif op == "MOD":
            self.reg[reg_a] %= self.reg[reg_b]
        elif op == "AND":
            self.reg[reg_a] &= self.reg[reg_b]
        elif op == "OR":
            self.reg[reg_a] |= self.reg[reg_b]
        elif op == "NOT":
            # calculate bitwise not with XOR mask
            self.reg[reg_a] ^= 0b11111111
        elif op == "CMP":
            diff = self.reg[reg_a] - self.reg[reg_b]
            if diff < 0:
                self.FL = 0b100
            elif diff > 0:
                self.FL = 0b10
            else:
                self.FL = 0b1
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def HLT(self):
        self.running = False

    def LDI(self, reg_index, value):
        self.mar = reg_index
        self.mdr = value
        self.ram_write()

    def LD(self, reg_a, reg_b):
        self.mar = reg_a
        self.mdr = self.reg[reg_b]
        self.ram_write()

    def PRN(self, reg_index):
        self.mar = reg_index
        print(self.ram_read())

    def run(self):
        """Run the CPU."""
        while self.running:
            # grab the IR
            ir = self.ram[self.pc]

            # pull out the relevant data to be processed
            instruction_code = ir & 0b1111
            setsPC = (ir >> 4) & 0b1
            isALU = (ir >> 5) & 0b1
            num_args = ir >> 6

            # if it's an alu function, process it through the alu
            if num_args == 0:
                if isALU:
                    self.alu(self.alutable[instruction_code])
                else:
                    if instruction_code != 0:
                        self.branchtable[instruction_code]()
            elif num_args == 1:
                arg_a = self.ram[self.pc + 1]
                if isALU:
                    self.alu(self.alutable[instruction_code], arg_a)
                else:
                    self.branchtable[instruction_code](arg_a)
            elif num_args == 2:
                arg_a = self.ram[self.pc + 1]
                arg_b = self.ram[self.pc + 2]
                if isALU:
                    self.alu(self.alutable[instruction_code], arg_a, arg_b)
                else:
                    self.branchtable[instruction_code](arg_a, arg_b)

            # after any process, increment the pc
            self.pc += num_args + 1
