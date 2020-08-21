import sys
from utils import flush_input
from pynput import keyboard
from datetime import datetime


class CPU:
    def __init__(self):
        # Data Storage
        self.ram = [0] * 256
        self.reg = [0] * 8

        # program pointer
        self.pc = 0

        # ram edit values?
        # self.mar = 0
        # self.mdr = 0
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

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, address, value):
        self.ram[address] = value

    def load(self, prog_file):
        program = []
        try:
            with open(prog_file) as f:
                for line in f:
                    x = line.split()
                    if len(x) == 0 or x[0][0] == "#":
                        continue

                    try:
                        program.append(int(x[0], 2))
                    except ValueError:
                        print(f"Invalid value: {x[0]}")
                        self.running = False
                        break
        except FileNotFoundError:
            self.running = False
            print(f"Couldn't open file: {prog_file}")

        address = 0
        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def PUSH(self, reg_index, *args):
        value = self.reg[reg_index]
        self.reg[self.SP] -= 1
        self.ram_write(self.reg[self.SP], value)

    def POP(self, reg_index, *args):
        value = self.ram_read(self.reg[self.SP])
        self.reg[self.SP] += 1
        self.reg[reg_index] = value

    def alu(self, op, reg_a=None, reg_b=None):
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

    def HLT(self, *args):
        self.running = False

    def LDI(self, reg_index, value):
        self.reg[reg_index] = value

    def LD(self, reg_a, reg_b):
        self.reg[reg_a] = self.ram_read(self.reg[reg_b])

    def ST(self, reg_a, reg_b):
        self.ram_write(self.reg[reg_a], self.reg[reg_b])

    def PRN(self, reg_index, *args):
        print(self.reg[reg_index])

    def PRA(self, reg_index, *args):
        print(chr(self.reg[reg_index]))

    # Jump Methods
    def CALL(self, reg_index, *args):
        next_index = self.pc + 2
        self.pc = self.reg[reg_index]
        self.reg[self.SP] -= 1
        self.ram_write(self.reg[self.SP], next_index)

    def RET(self, *args):
        self.pc = self.ram_read(self.reg[self.SP])
        self.reg[self.SP] += 1

    def JMP(self, reg_index, *args):
        self.pc = self.reg[reg_index]

    def JNE(self, reg_index, *args):
        test = 0b001
        if self.FL != test:
            self.pc = self.reg[reg_index]
        else:
            self.pc += 2

    def JEQ(self, reg_index, *args):
        test = 0b001
        if self.FL & test > 0:
            self.pc = self.reg[reg_index]
        else:
            self.pc += 2

    def JGT(self, reg_index, *args):
        test = 0b010
        if self.FL & test > 0:
            self.pc = self.reg[reg_index]
        else:
            self.pc += 2

    def JGE(self, reg_index, *args):
        test = 0b011
        if self.FL & test > 0:
            self.pc = self.reg[reg_index]
        else:
            self.pc += 2

    def JLT(self, reg_index, *args):
        test = 0b100
        if self.FL & test > 0:
            self.pc = self.reg[reg_index]
        else:
            self.pc += 2

    def JLE(self, reg_index, *args):
        test = 0b101
        if self.FL & test > 0:
            self.pc = self.reg[reg_index]
        else:
            self.pc += 2

    def INT(self, reg_index, *args):
        # For now, I can't use this
        pass

    def IRET(self, *args):
        # pop registers 6-0 off the stack in that order
        for i in range(7):
            self.reg[6 - i] = self.ram_read(self.reg[self.SP])
            self.reg[self.SP] += 1
        self.FL = self.ram_read(self.reg[self.SP])
        self.reg[self.SP] += 1
        self.pc = self.ram_read(self.reg[self.SP])
        self.reg[self.SP] += 1

    # Interrupt methods
    def timer_interrupt_check(self):
        x = datetime.now()
        if (x - self.time).seconds >= 1:
            self.time = x
            self.reg[self.IS] |= 0b00000001

    def keyboard_listener_start(self):
        # keypress handler that sets the proper IS bit
        def on_press(key):
            if key == keyboard.Key.esc:
                self.running = False
            else:
                if str(key)[:4] != "Key.":
                    if (str(key)[0] == "<" and str(key)[-1] == ">"):
                        return
                    self.reg[self.IS] |= 0b00000010
                    x = ord(str(key)[1])
                    self.ram_write(0xf4, x & 255)
        # keyboard listener start code
        self.keyboard_listener = keyboard.Listener(on_press=on_press)
        self.keyboard_listener.start()

    def keyboard_listener_stop(self):
        self.keyboard_listener.stop()

    def check_interrupt_status(self):
        # interrupt checking
        if self.reg[self.IS] != 0:
            masked_interrupts = self.reg[self.IM] & self.reg[self.IS]
            cur_bit = 0
            interrupted = False
            while cur_bit < 8 and not interrupted:
                interrupted = ((masked_interrupts >> cur_bit) & 1) == 1
                if interrupted:
                    # clear the bit
                    self.reg[self.IS] ^= 1 << cur_bit
                    # push PC onto stack
                    self.reg[self.SP] -= 1
                    self.ram_write(self.reg[self.SP], self.pc)
                    # push FL onto stack
                    self.reg[self.SP] -= 1
                    self.ram_write(self.reg[self.SP], self.FL)
                    # push R0-R6 onto stack in that order
                    for i in range(7):
                        self.reg[self.SP] -= 1
                        self.ram_write(self.reg[self.SP], self.reg[i])
                    self.pc = self.ram_read(0xF8 + cur_bit)
                cur_bit += 1

    def run(self):
        # Initialize CPU properties for interrupts
        self.time = datetime.now()
        self.keyboard_listener_start()

        # instruction fetch
        while self.running:
            self.check_interrupt_status()
            self.timer_interrupt_check()

            # grab the IR
            ir = self.ram[self.pc]

            # pull out the relevant data from the IR to be processed
            instruction_code = ir & 0b1111
            setsPC = (ir >> 4) & 0b1
            isALU = (ir >> 5) & 0b1
            num_args = ir >> 6

            # if it's an alu function, process it through the alu
            # if it's a jump function, process accordingly
            arg_a = self.ram[self.pc + 1]
            arg_b = self.ram[self.pc + 2]
            if isALU:
                self.alu(self.alutable[instruction_code], arg_a, arg_b)
            elif setsPC:
                self.jumptable[instruction_code](arg_a, arg_b)
            else:
                if instruction_code != 0:
                    self.branchtable[instruction_code](arg_a, arg_b)

            # after a process that doesn't set PC, increment the pc
            if not setsPC:
                self.pc += num_args + 1

        # clear listener after while loop ends
        self.keyboard_listener_stop()

        # clear the input buffer to handle presses in peyboard interrupt test
        flush_input()
