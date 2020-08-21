"""
CPU functionality.

methods needed to implement:
JEQ
JGE
JGT
JLE
JMP
JNE
INT
"""

import sys
from utils import flush_input
from pynput import keyboard
from datetime import datetime


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8

        # program pointer
        self.pc = 0

        # ram edit values?
        self.mar = 0
        self.mdr = 0
        self.running = True

        # set comparison flags default to 0 (last 3 bits are L, G, E)
        self.FL = 0b00000000

        # alu operation table
        self.alutable = {}
        self.alutable[0b0000] = "ADD"
        self.alutable[0b0001] = "SUB"
        self.alutable[0b0010] = "MUL"
        self.alutable[0b0011] = "DIV"
        self.alutable[0b0100] = "MOD"
        self.alutable[0b0101] = "INC"
        self.alutable[0b0110] = "DEC"
        self.alutable[0b0111] = "CMP"
        self.alutable[0b1000] = "AND"
        self.alutable[0b1001] = "NOT"
        self.alutable[0b1010] = "OR"
        self.alutable[0b1011] = "XOR"
        self.alutable[0b1100] = "SHL"
        self.alutable[0b1101] = "SHR"

        # jump functions
        self.jumptable = {}
        self.jumptable[0b0000] = self.CALL
        self.jumptable[0b0001] = self.RET
        self.jumptable[0b0010] = self.INT
        self.jumptable[0b0011] = self.IRET
        self.jumptable[0b0100] = self.JMP
        self.jumptable[0b0101] = self.JEQ
        self.jumptable[0b0110] = self.JNE
        self.jumptable[0b0111] = self.JGT
        self.jumptable[0b1000] = self.JLT
        self.jumptable[0b1001] = self.JLE
        self.jumptable[0b1010] = self.JGE

        # non-alu instruction definitions
        self.branchtable = {}
        self.branchtable[0b0001] = self.HLT
        self.branchtable[0b0010] = self.LDI
        self.branchtable[0b0011] = self.LD
        self.branchtable[0b0100] = self.ST
        self.branchtable[0b0101] = self.PUSH
        self.branchtable[0b0110] = self.POP
        self.branchtable[0b0111] = self.PRN
        self.branchtable[0b1000] = self.PRA

        # Interrupt properties
        self.time = None  # init with datetime.now() on run to handle timer interrupt
        self.keyboard_listener = None

        # reserved register addresses
        self.IM = 5
        self.IS = 6
        self.SP = 7

        # initialize reserved registers
        self.reg[self.IM] = 0b00000001
        self.reg[self.IS] = 0b00000000
        self.reg[self.SP] = 0xF4

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

    def PUSH(self, reg_index):
        # print(self.ram[0xf0:0xf4])

        self.mar = reg_index
        value = self.ram_read()
        # print(reg_index, value)
        self.reg[self.SP] -= 1
        self.ram[self.reg[self.SP]] = value

    def POP(self, reg_index):
        # print(self.ram[0xf0:0xf4])
        self.mar = reg_index
        self.mdr = self.ram[self.reg[self.SP]]
        self.reg[self.SP] += 1
        self.ram_write()

    def alu(self, op, reg_a=None, reg_b=None):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
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
        elif op == "XOR":
            self.reg[reg_a] ^= self.reg[reg_b]
        elif op == "SHL":
            self.reg[reg_a] <<= self.reg[reg_b]
        elif op == "SHR":
            self.reg[reg_a] >>= self.reg[reg_b]
        elif op == "CMP":
            diff = self.reg[reg_a] - self.reg[reg_b]
            if diff < 0:
                self.FL = 0b100
            elif diff > 0:
                self.FL = 0b010
            else:
                self.FL = 0b001
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
        # print(self.ram[:5])
        self.mar = reg_a
        self.mdr = self.ram[self.reg[reg_b]]
        self.ram_write()

    def ST(self, reg_a, reg_b):
        # print(f"{reg_a}: {self.reg[reg_a]}")
        # print(f"{reg_b}: {self.reg[reg_b]}")
        # print(bin(self.reg[reg_a]), bin(self.reg[self.SP]))
        self.ram[self.reg[reg_a]] = self.reg[reg_b]

    def PRN(self, reg_index):
        self.mar = reg_index
        print(self.ram_read())

    def PRA(self, reg_index):
        self.mar = reg_index
        print(chr(self.ram_read()))

    # Jump Methods
    def CALL(self, reg_index):
        # push the next instruction's index onto the stack
        next_index = self.pc + 2
        self.reg[self.SP] -= 1
        self.ram[self.reg[self.SP]] = next_index
        self.pc = self.reg[reg_index]

    def RET(self):
        # print("b4: ", self.pc)
        self.pc = self.ram[self.reg[self.SP]]
        # print("af: ", self.pc)
        self.reg[self.SP] += 1

    def JMP(self, reg_index):
        # print(reg_index, self.reg, self.ram[self.reg[self.SP]])
        self.pc = self.reg[reg_index]

    def JNE(self, reg_index):
        test = 0b000
        if self.FL | test == 0:
            self.pc = self.reg[reg_index]
        else:
            self.pc += 2

    def JEQ(self, reg_index):
        test = 0b001
        if self.FL & test > 0:
            self.pc = self.reg[reg_index]
        else:
            self.pc += 2

    def JGT(self, reg_index):
        test = 0b010
        if self.FL & test > 0:
            self.pc = self.reg[reg_index]
        else:
            self.pc += 2

    def JGE(self, reg_index):
        test = 0b011
        if self.FL & test > 0:
            self.pc = self.reg[reg_index]
        else:
            self.pc += 2

    def JLT(self, reg_index):
        test = 0b100
        if self.FL & test > 0:
            self.pc = self.reg[reg_index]
        else:
            self.pc += 2

    def JLE(self, reg_index):
        test = 0b101
        if self.FL & test > 0:
            self.pc = self.reg[reg_index]
        else:
            self.pc += 2

    def INT(self, reg_index):
        # bitwise OR to set the flag for whatever interrupt happened
        # self.reg[self.IS] |= (2 ** (self.reg[reg_index] - 1))
        self.reg[self.IS] |= 1 << self.reg[reg_index] - 1

    def IRET(self):
        # pop registers 6-0 off the stack in that order
        for i in range(7):
            self.mar = 6 - i
            self.mdr = self.ram[self.reg[self.SP]]
            self.reg[self.SP] += 1
            self.ram_write()
        self.FL = self.ram[self.reg[self.SP]]
        self.reg[self.SP] += 1
        self.pc = self.ram[self.reg[self.SP]]
        self.reg[self.SP] += 1

    # interrupt methods?
    def timer_interrupt_check(self):
        x = datetime.now()
        if (x - self.time).seconds >= 1:
            self.time = x
            self.reg[self.IS] |= 0b00000001

    def keyboard_listener_start(self):
        # keypress handler that sets the IS bit
        def on_press(key):
            if key == keyboard.Key.esc:
                self.running = False
            else:
                if str(key)[:4] != "Key.":
                    if (str(key)[0] == "<" and str(key)[-1] == ">"):
                        return
                    self.reg[self.IS] |= 0b00000010
                    x = ord(str(key)[1])
                    self.ram[0xf4] = x & 255

        # keyboard listener start code
        self.keyboard_listener = keyboard.Listener(
            on_press=on_press
        )
        self.keyboard_listener.start()

    def keyboard_listener_stop(self):
        self.keyboard_listener.stop()

    def run(self):
        # time init for interrupt checking
        self.time = datetime.now()
        self.keyboard_listener_start()

        # printvals = {x: y for x, y in enumerate(self.ram[0:40])}

        # print(printvals)

        # instruction fetch
        while self.running:
            # print(self.ram[self.reg[self.SP]])

            # interrupt checking
            if self.reg[self.IS] != 0:
                masked_interrupts = self.reg[self.IM] & self.reg[self.IS]
                cur_bit = 0
                interrupted = False
                while cur_bit < 8 and not interrupted:
                    interrupted = ((masked_interrupts >> cur_bit) & 1) == 1
                    if interrupted:
                        # print(self.pc, self.ram[self.pc])
                        # clear the bit
                        self.reg[self.IS] ^= 1 << cur_bit

                        # push PC onto stack
                        self.reg[self.SP] -= 1
                        self.ram[self.reg[self.SP]] = self.pc
                        # push FL onto stack
                        self.reg[self.SP] -= 1
                        self.ram[self.reg[self.SP]] = self.FL
                        # push R0-R6 onto stack in that order
                        for i in range(7):
                            self.reg[self.SP] -= 1
                            self.ram[self.reg[self.SP]] = self.reg[i]
                        self.pc = self.ram[0xF8 + cur_bit]
                    cur_bit += 1

            self.timer_interrupt_check()

            # grab the IR
            # print(self.pc)
            ir = self.ram[self.pc]
            # print(bin(self.FL), bin(ir))
            # pull out the relevant data to be processed
            instruction_code = ir & 0b1111
            setsPC = (ir >> 4) & 0b1
            isALU = (ir >> 5) & 0b1
            num_args = ir >> 6
            # print(instruction_code, num_args)

            # if it's an alu function, process it through the alu
            # if it's a jump function, process accordingly
            if num_args == 0:
                if isALU:
                    self.alu(self.alutable[instruction_code])
                elif setsPC:
                    self.jumptable[instruction_code]()
                else:
                    if instruction_code != 0:
                        # skips NOP lines in program while still incrementing pc
                        self.branchtable[instruction_code]()
            elif num_args == 1:
                arg_a = self.ram[self.pc + 1]
                if isALU:
                    self.alu(self.alutable[instruction_code], arg_a)
                elif setsPC:
                    self.jumptable[instruction_code](arg_a)
                else:
                    self.branchtable[instruction_code](arg_a)
            elif num_args == 2:
                arg_a = self.ram[self.pc + 1]
                arg_b = self.ram[self.pc + 2]
                if isALU:
                    self.alu(self.alutable[instruction_code], arg_a, arg_b)
                elif setsPC:
                    self.jumptable[instruction_code](arg_a, arg_b)
                else:
                    self.branchtable[instruction_code](arg_a, arg_b)

            # after a process that doesn't set PC, increment the pc
            if not setsPC:
                self.pc += num_args + 1

        self.keyboard_listener_stop()

        # clear the input buffer to handle presses in peyboard interrupt test
        flush_input()
