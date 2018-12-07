import tkinter as tk
import random
import time
import os
import threading

if os.name == "nt":
    import winsound
    def beep(freq, dur):
        threading.Thread(target=lambda: winsound.Beep(freq, dur)).start()
else:
    def beep(freq, dur):
        pass

G_WIDTH = 15
G_HEIGHT = 15
G_SIDE = 20
G_SPEED = 9

G_SNAKE_COLOR = "blue"
G_FOOD_COLOR = "green"
G_GAME_OVER_COLOR = "red"


class SnakeCore:
    def __init__(self, width, height, wait):
        self._width = width
        self._height = height
        self._wait = wait
        self.reset()

    @property
    def body(self):
        return self._body

    @property
    def food(self):
        return self._food

    @property
    def game_over(self):
        return self._game_over

    def reset(self):
        self._game_over = False
        self._body = [[2,1], [1,1]]
        self._direction = "right"
        self._generate_food()
        self._block_direction = False

    def _generate_food(self):
        while True:
            self._food = [random.randint(0, self._width - 1), random.randint(0, self._height - 1)]
            if self._food not in self.body:
                break

    def set_direction(self, direction):
        if direction == "left" and self._direction == "right": return
        if direction == "right" and self._direction == "left": return
        if direction == "up" and self._direction == "down": return
        if direction == "down" and self._direction == "up": return
        if not self._block_direction:
            self._direction = direction
            self._block_direction = True

    def move(self):
        body = self.body
        head = body[0][:]
        if self._direction == "left": head[0] -= 1
        elif self._direction == "right": head[0] += 1
        elif self._direction == "up": head[1] -= 1
        elif self._direction == "down": head[1] += 1
        if head in self.body or head[0] == -1 or head[1] == -1 or head[0] == self._width or head[1] == self._height:
            self._game_over = True
            return False
        self._block_direction = False
        if head[0] == self.food[0] and head[1] == self.food[1]:
            body.insert(0, self.food)
            self._generate_food()
            return True
        else:
            body.insert(0, head)
            del body[-1]
        return False


class Snake:
    def __init__(self, width, height, side, speed):
        self._root = tk.Tk()
        self._frame = tk.Frame(self._root)
        self._canvas = tk.Canvas(self._root, width=width*side-1, height=height*side-1, highlightthickness=1, highlightbackground="black")
        self._canvas.pack()
        self._frame.pack()
        self._root.resizable(0,0)
        self._root.wm_title("Snake")
        self._cong = False
        self._width = width
        self._height = height
        self._side = side
        self._wait = 0

        self._snake_core = SnakeCore(width, height, 0)

        self._squares = [[None for y in range(self._height)] for x in range(self._width)]
        self._squares_prev = [[None for y in range(self._height)] for x in range(self._width)]

        self._new_but = tk.Button(self._frame, text="New", command=self._reset)
        self._down_speed_but = tk.Button(self._frame, text="-", command=self._down_speed)
        self._up_speed_but = tk.Button(self._frame, text="+", command=self._up_speed)
        self._speed_lbl = tk.Label(self._frame)

        self._new_but.grid(row=0, column=0, padx=50)
        self._down_speed_but.grid(row=0, column=1)
        self._up_speed_but.grid(row=0, column=2)
        self._speed_lbl.grid(row=0, column=3, padx=5)

        self._root.bind("<Left>", self._leftKey)
        self._root.bind("<Right>", self._rightKey)
        self._root.bind("<Up>", self._upKey)
        self._root.bind("<Down>", self._downKey)

        self._set_speed(speed)
        self._mutex = threading.Lock()

    def _move(self, direction):
        if not self._snake_core.game_over:
            self._snake_core.set_direction(direction)

    @staticmethod
    def _speed_to_wait(speed):
        return 1 - (speed-1) * 0.1
    def _set_speed(self, speed):
        self._speed = speed
        self._wait = Snake._speed_to_wait(speed)
        self._speed_lbl["text"] = str(self._speed)

    def _leftKey(self, event): self._move("left")
    def _rightKey(self, event): self._move("right")
    def _upKey(self, event): self._move("up")
    def _downKey(self, event): self._move("down")

    def run(self):
        threading.Thread(target=self._run).start()
        self._root.mainloop()

    def _run(self):
        snake_core = self._snake_core
        stop = False
        while not stop:
            if snake_core.game_over:
                stop = True
            self._draw()
            time.sleep(self._wait)
            bp = (100, 30)
            if snake_core.move():
                bp = (200, 200)
            elif snake_core.game_over:
                bp = (300, 750)
            if not stop:
                beep(bp[0], bp[1])

    def _draw_square(self, square, color="white"):
        x, y, side = square[0], square[1], self._side
        self._canvas.create_rectangle(x*side, y*side, (x+1)*side, (y+1)*side, fill=color)

    def _prepare_draw(self):
        snake_core = self._snake_core
        self._squares_prev = self._squares.copy()
        self._squares = [[self._canvas["background"] for y in range(self._height)] for x in range(self._width)]
        snake_color = G_GAME_OVER_COLOR if snake_core.game_over else G_SNAKE_COLOR
        for square in snake_core.body:
            self._squares[square[0]][square[1]] = snake_color
        self._squares[snake_core.food[0]][snake_core.food[1]] = G_FOOD_COLOR

    def _draw(self):
        self._prepare_draw()
        for x in range(self._width):
            for y in range(self._height):
                square = self._squares[x][y]
                square_prev = self._squares_prev[x][y]
                color = self._squares[x][y]
                if color != self._squares_prev[x][y]:
                    self._draw_square([x,y], color)

    def _reset(self):
        if self._mutex.locked(): return
        beep(700, 75)
        game_over = self._snake_core.game_over
        self._snake_core.reset()
        if game_over:
            self.run()

    def _down_speed(self):
        if self._speed > 1:
            beep(700, 75)
            self._set_speed(self._speed - 1)

    def _up_speed(self):
        if self._speed < 10:
            beep(700, 75)
            self._set_speed(self._speed + 1)


if __name__ == "__main__":
    snake = Snake(G_WIDTH, G_HEIGHT, G_SIDE, G_SPEED)
    snake.run()
