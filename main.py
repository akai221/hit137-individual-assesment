# main.py
# HIT137 Assignment 3 - tile puzzle game
# run: python main.py

import base64
import random
import tkinter as tk
from tkinter import filedialog, messagebox
import cv2

from puzzle import Board

SIZE = 480


# load image, resize and crop it to a square
def load_image(path, grid):
    img = cv2.imread(path)
    if img is None:
        return None
    h, w = img.shape[:2]
    scale = SIZE / min(h, w)
    img = cv2.resize(img, (max(SIZE, int(w*scale)), max(SIZE, int(h*scale))))
    side = (SIZE // grid) * grid
    h, w = img.shape[:2]
    top = (h - side) // 2
    left = (w - side) // 2
    return img[top:top+side, left:left+side]


def to_photo(img):
    ok, data = cv2.imencode(".png", img)
    return tk.PhotoImage(data=base64.b64encode(data))


class App:
    def __init__(self, root):
        self.root = root
        root.title("Tile Puzzle")
        self.board = None
        self.grid = tk.IntVar(value=3)

        top = tk.Frame(root)
        top.pack()
        tk.Button(top, text="Load Image", command=self.load).pack(side="left")
        for g in [3, 4, 5]:
            tk.Radiobutton(top, text=f"{g}x{g}", variable=self.grid, value=g).pack(side="left")
        self.hint_btn = tk.Button(top, text="Hint", command=self.hint)
        self.hint_btn.pack(side="left")
        tk.Button(top, text="Solve", command=self.solve).pack(side="left")

        frame = tk.Frame(root)
        frame.pack()
        self.left = tk.Canvas(frame, width=SIZE, height=SIZE, bg="white")
        self.left.pack(side="left")
        self.right = tk.Canvas(frame, width=SIZE, height=SIZE, bg="white")
        self.right.pack(side="left")

        self.label = tk.Label(root, text="Load an image to start")
        self.label.pack()

        self.right.bind("<Button-1>", self.left_click)
        self.right.bind("<Shift-Button-1>", self.shift_click)
        self.right.bind("<Button-3>", self.right_click)

    def load(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp")])
        if path == "":
            return
        img = load_image(path, self.grid.get())
        if img is None:
            messagebox.showerror("Error", "Could not open that file as an image")
            return
        self.board = Board(img, self.grid.get())
        self.board.scramble()
        self.hint_btn.config(state="normal")
        self.draw()

    def get_pos(self, event):
        if self.board is None or self.board.done:
            return None
        s = self.board.size
        if event.x >= s * self.board.grid or event.y >= s * self.board.grid:
            return None
        return (event.y // s) * self.board.grid + event.x // s

    def left_click(self, event):
        pos = self.get_pos(event)
        if pos is None:
            return
        b = self.board
        if b.selected is None:
            b.selected = pos
        elif b.selected == pos:
            b.selected = None
        else:
            b.swap(b.selected, pos)
            b.selected = None
            b.after_move()
        self.draw()

    def right_click(self, event):
        pos = self.get_pos(event)
        if pos is None:
            return
        self.board.tiles[pos].rotate()
        self.board.after_move()
        self.draw()

    def shift_click(self, event):
        pos = self.get_pos(event)
        if pos is None:
            return
        self.board.tiles[pos].flip()
        self.board.after_move()
        self.draw()

    def hint(self):
        if self.board is None or self.board.done or self.board.hints == 0:
            return
        self.board.hint = random.choice(self.board.wrong_tiles())
        self.board.hints -= 1
        if self.board.hints == 0:
            self.hint_btn.config(state="disabled")
        self.draw()

    def solve(self):
        if self.board is None:
            return
        self.board.solve()
        self.draw()

    def draw(self):
        b = self.board
        s = b.size
        self.left.delete("all")
        self.right.delete("all")
        self.photo1 = to_photo(b.original)
        self.photo2 = to_photo(b.get_image())
        self.left.create_image(0, 0, anchor="nw", image=self.photo1)
        self.right.create_image(0, 0, anchor="nw", image=self.photo2)

        for i in range(1, b.grid):
            self.right.create_line(i*s, 0, i*s, s*b.grid, fill="lightgrey")
            self.right.create_line(0, i*s, s*b.grid, i*s, fill="lightgrey")

        for pos in range(b.grid * b.grid):
            x = (pos % b.grid) * s
            y = (pos // b.grid) * s
            if b.correct(pos):
                self.right.create_line(x+s-20, y+10, x+s-14, y+16, x+s-5, y+5, fill="green", width=3)
            if pos == b.selected:
                self.right.create_rectangle(x, y, x+s, y+s, outline="red", width=3)
            if pos == b.hint:
                self.right.create_oval(x+s/4, y+s/4, x+3*s/4, y+3*s/4, outline="blue", width=3)
                home = b.tiles[pos].home
                hx = (home % b.grid) * s
                hy = (home // b.grid) * s
                self.left.create_oval(hx+s/4, hy+s/4, hx+3*s/4, hy+3*s/4, outline="blue", width=3)

        self.label.config(text=f"Moves: {b.moves}   Tiles left: {len(b.wrong_tiles())}   Hints left: {b.hints}")
        if b.done:
            self.hint_btn.config(state="disabled")
            if len(b.wrong_tiles()) == 0 and b.moves > 0:
                messagebox.showinfo("Done", f"You solved it in {b.moves} moves!")


root = tk.Tk()
App(root)
root.mainloop()
