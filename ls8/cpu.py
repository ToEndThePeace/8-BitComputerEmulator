"""CPU functionality."""

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

        # instruction definitions
        self.HLT = 1
        self.LDI = 130
        self.PRN = 71
        self.MUL = 162

    def ram_read(self):
        return self.reg[self.mar]

    def ram_write(self):
        self.reg[self.mar] = self.mdr

    def load(self, program):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111,  # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
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

    def run(self):
        """Run the CPU."""
        running = True

        while running:
            ir = self.ram[self.pc]
            # print(ir)
            if ir == self.HLT:
                # print("HLT")
                running = False
                self.pc += 1
            elif ir == self.LDI:
                # print("LDI")
                # load the arguments into the proper registers
                self.mar = self.ram[self.pc + 1]
                self.mdr = self.ram[self.pc + 2]
                # update CPU with the stored data
                self.ram_write()
                # increment our program counter
                self.pc += 3
            elif ir == self.PRN:
                # print("PRN")
                # load the argument into the register
                self.mar = self.ram[self.pc + 1]
                # print out the value at the register
                print(self.ram_read())
                self.pc += 2
            elif ir == self.MUL:
                a = self.ram[self.pc + 1]
                b = self.ram[self.pc + 2]
                self.alu("MUL", a, b)

                self.pc += 3
            else:
                print("Invalid function call. Exiting...")
                running = False
