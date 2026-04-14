import random
import tkinter as tk
from tkinter import filedialog

# =========================================================
# CHIP-8 EMULATOR (SINGLE FILE)
# =========================================================

class Chip8:
    def __init__(self):
        self.mem = [0] * 4096
        self.V = [0] * 16
        self.I = 0
        self.pc = 0x200
        self.stack = []

        self.gfx = [0] * (64 * 32)
        self.keys = [0] * 16

        self.running = False
        self.load_font()

    def load_font(self):
        font = [
            0xF0,0x90,0x90,0x90,0xF0,
            0x20,0x60,0x20,0x20,0x70,
            0xF0,0x10,0xF0,0x80,0xF0,
            0xF0,0x10,0xF0,0x10,0xF0,
            0x90,0x90,0xF0,0x10,0x10,
            0xF0,0x80,0xF0,0x10,0xF0,
            0xF0,0x80,0xF0,0x90,0xF0,
            0xF0,0x10,0x20,0x40,0x40,
            0xF0,0x90,0xF0,0x90,0xF0,
            0xF0,0x90,0xF0,0x10,0xF0,
            0xF0,0x90,0xF0,0x90,0x90,
            0xE0,0x90,0xE0,0x90,0xE0,
            0xF0,0x80,0x80,0x80,0xF0,
            0xE0,0x90,0x90,0x90,0xE0,
            0xF0,0x80,0xF0,0x80,0xF0,
            0xF0,0x80,0xF0,0x80,0x80
        ]
        for i, b in enumerate(font):
            self.mem[0x50 + i] = b

    def load_rom(self, path):
        with open(path, "rb") as f:
            rom = f.read()
        for i, b in enumerate(rom):
            self.mem[0x200 + i] = b
        self.pc = 0x200
        self.gfx = [0] * (64 * 32)

    def step(self):
        op = (self.mem[self.pc] << 8) | self.mem[self.pc + 1]
        self.pc += 2

        x = (op >> 8) & 0xF
        y = (op >> 4) & 0xF
        n = op & 0xF
        nn = op & 0xFF
        nnn = op & 0xFFF

        if op == 0x00E0:
            self.gfx = [0] * 2048

        elif (op & 0xF000) == 0x1000:
            self.pc = nnn

        elif (op & 0xF000) == 0x6000:
            self.V[x] = nn

        elif (op & 0xF000) == 0x7000:
            self.V[x] = (self.V[x] + nn) & 0xFF

        elif (op & 0xF000) == 0xA000:
            self.I = nnn

        elif (op & 0xF000) == 0xD000:
            self.V[0xF] = 0
            for row in range(n):
                sprite = self.mem[self.I + row]
                for col in range(8):
                    if sprite & (0x80 >> col):
                        px = (self.V[x] + col) % 64
                        py = (self.V[y] + row) % 32
                        idx = px + py * 64
                        self.V[0xF] |= self.gfx[idx]
                        self.gfx[idx] ^= 1

        elif (op & 0xF000) == 0xC000:
            self.V[x] = random.randint(0, 255) & nn


# =========================================================
# UI
# =========================================================

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # ✅ FIXED TITLE (as requested)
        self.title("ChatGPT's Chip-8 Emulator")

        self.chip8 = Chip8()

        self.canvas = tk.Canvas(self, width=640, height=320, bg="black")
        self.canvas.grid(row=0, column=0, columnspan=4)

        self.pixels = [
            self.canvas.create_rectangle(
                x*10, y*10, (x+1)*10, (y+1)*10,
                outline="", fill="black"
            )
            for y in range(32)
            for x in range(64)
        ]

        btn = lambda t, c: tk.Button(self, text=t, bg="blue", fg="black", command=c)

        btn("Load", self.load).grid(row=1, column=0)
        btn("Run", self.run).grid(row=1, column=1)
        btn("Step", self.step).grid(row=1, column=2)
        btn("Reset", self.reset).grid(row=1, column=3)

        self.after(10, self.loop)

    def load(self):
        path = filedialog.askopenfilename()
        if path:
            self.chip8.load_rom(path)

    def run(self):
        self.chip8.running = True

    def step(self):
        self.chip8.step()
        self.draw()

    def reset(self):
        self.chip8 = Chip8()

    def loop(self):
        if self.chip8.running:
            for _ in range(6):
                self.chip8.step()
            self.draw()
        self.after(10, self.loop)

    def draw(self):
        for i, v in enumerate(self.chip8.gfx):
            self.canvas.itemconfig(self.pixels[i], fill="white" if v else "black")


# =========================================================
# RUN
# =========================================================

App().mainloop()
