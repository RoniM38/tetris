import turtle
import random
import time
import shapes # the list of shapes
import pygame # for sounds
pygame.mixer.init()

window = turtle.Screen()
window.title("Tetris")
window.setup(600, 600, 340, 20)
turtle.delay(0)

text_turtle = turtle.Turtle()
score_turtle = turtle.Turtle()
lose_turtle = turtle.Turtle()
turtles = (text_turtle, score_turtle, lose_turtle)

for t in turtles:
    t.hideturtle()
    t.penup()
    t.speed(0)

BLACK = (0, 0, 0)
PIXEL_SIZE = 20
PEN_SIZE = 2.5

colors_list = ("red", "orange", "yellow", "green", "blue", "cyan", "purple", "pink")
score = 0


class Block:
    def __init__(self, shape, shape_color, row, column, board):
        self.shape = shape
        self.shape_color = shape_color
        self.row = row - 1
        self.column = column - 1
        self.board = board

        self.width = 0
        self.height = 0

        self.state_index = 0
        self.state = shape[self.state_index]
        self.left_gap = min([st.index("0") for st in self.state]) + (self.width - 1)
        self.right_gap = len(self.state[0]) - max([st.rindex("0") for st in self.state]) - 1

        self.pixels = []
        self.moving = True

        self.score = score

    def draw(self):
        self.pixels.clear()
        for i, rows in enumerate(self.state):
            for j, c in enumerate(rows):
                pixel = self.board.pixels[self.row - i][self.column - j]

                if c == "0":
                    color = self.shape_color
                else:
                    if any(pixel in block.pixels for block in self.board.blocks):
                        color = pixel.fill_color
                    else:
                        color = "white"

                pixel.fill_color = color
                if color == self.shape_color:
                    self.pixels.append(pixel)

        columns = [pixel.column for pixel in self.pixels]
        self.width = max(columns) - min(columns) + 1

        rows = [pixel.row for pixel in self.pixels]
        self.height = max(rows) - min(rows) + 1

        self.left_gap = min((st.index("0") for st in self.state)) + (self.width - 1)
        self.right_gap = len(self.state[0]) - max((st.rindex("0") for st in self.state)) - 1

    def min_pixel(self):
        lowest_pixel = self.pixels[0]
        for pixel in self.pixels:
            if pixel.row < lowest_pixel.row:
                lowest_pixel = pixel
        return lowest_pixel

    def collision(self):
        global score

        lowest_pixel = self.min_pixel()

        if self.board.pixels[lowest_pixel.row - 1][lowest_pixel.column].colored or \
                lowest_pixel.row == 0:
            score += 5

            if self.row >= self.board.height - 2:
                self.board.game_over = True
                losing_sound = pygame.mixer.Sound("Sounds/game_over.wav")
                losing_sound.play()

            return True

    def rotate(self):
        if self.state_index < len(self.shape)-1:
            self.state_index += 1
        else:
            self.state_index = 0

        for pixel in self.pixels:
            pixel.fill_color = "white"
        self.pixels.clear()
        self.state = self.shape[self.state_index]
        self.draw()

    def move_left(self):
        if self.column - self.left_gap - 1 >= 0 and self.moving:
            self.column -= 1
            self.draw()

    def move_right(self):
        if self.column - self.right_gap - 1 < len(self.board.pixels[0]) - self.width + 1 and \
                self.moving:
            self.column += 1
            self.draw()

    def move_down(self):
        self.moving = not self.collision()

        if self.moving:
            for p in reversed(self.pixels):
                p.move_down(self.shape_color)
            self.row -= 1


class Pixel:
    def __init__(self, row, column, x, y, width, height, fill_color, board):
        self.row = row
        self.column = column
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.fill_color = fill_color
        self.board = board

        self.pixel_turtle = turtle.Turtle()
        self.pixel_turtle.hideturtle()
        self.pixel_turtle.speed(0)

        self.colored = self.fill_color != "white"

    def draw(self):
        self.colored = self.fill_color != "white"

        self.pixel_turtle.pensize(PEN_SIZE)
        self.pixel_turtle.pencolor("black")
        self.pixel_turtle.penup()
        self.pixel_turtle.goto(self.x, self.y)

        self.pixel_turtle.pendown()
        self.pixel_turtle.fillcolor(self.fill_color)
        self.pixel_turtle.begin_fill()

        for i in range(2):
            self.pixel_turtle.forward(self.width)
            self.pixel_turtle.right(90)
            self.pixel_turtle.forward(self.height)
            self.pixel_turtle.right(90)
        self.pixel_turtle.end_fill()

    def move_down(self, color):
        self.fill_color = "white"
        self.board.pixels[self.row-1][self.column].fill_color = color


class Board:
    def __init__(self, start_x, start_y, width, height, border_color, border_thickness):
        self.start_x = start_x
        self.start_y = start_y
        self.width = width
        self.height = height
        self.border_color = border_color
        self.border_thickness = border_thickness

        self.pixels = []
        self.blocks = []
        self.create_board()
        self.game_over = False

    def create_board(self):
        y = self.start_y
        for i in range(self.height):
            x = self.start_x
            j_pixels = []
            for j in range(self.width):
                x += PIXEL_SIZE
                j_pixels.append(Pixel(i, j, x, y, PIXEL_SIZE, PIXEL_SIZE, "white", self))
            self.pixels.append(j_pixels)
            y += PIXEL_SIZE

    def find_block(self, pixel):
        for block in self.blocks:
            if pixel in block.pixels:
                return block

    def draw(self):
        global score

        if len(self.blocks) == 0 or not any(block.moving for block in self.blocks) \
                and not self.game_over:
            shape = random.choice(shapes.shapes)
            shape_color = random.choice(colors_list)
            block = Block(shape, shape_color, self.height, 12, self)
            self.blocks.append(block)

        for pixel_list in self.pixels:
            flag = all(p.colored for p in pixel_list)
            for pixel in pixel_list:
                if flag:
                    b = self.find_block(pixel)
                    pixel.fill_color = "white"
                    if b is not None:
                        b.pixels.remove(pixel)
                        score += 20

                pixel.draw()

        for block in self.blocks:
            block.draw()


def display_score(high_score):
    global score

    if score > high_score:
        high_score = score
        with open("high_score.txt", "w") as f:
            f.write(str(high_score))

    score_turtle.clear()
    score_turtle.goto(-325, 200)
    text = '''
    SCORE:{}
    BEST:{}
    '''.format(score, high_score)
    score_turtle.write(text, font=("comicsans", 20, "bold"))


def main():
    global score
    score = 0

    with open("high_score.txt", "r") as f:
        high_score = int(f.read())

    window.tracer(0)

    wait_time = 0.1
    start = time.time()
    board = Board(-225, -255, 20, 25, BLACK, 2.5)

    text_turtle.pencolor(BLACK)

    music = pygame.mixer.Sound("Sounds/tetris_music.wav")
    music.play(-1)

    while True:
        text_turtle.goto(-100, 225)
        text_turtle.write("TETRIS", font=("comicsans", 45, "bold"))
        display_score(high_score)

        time.sleep(1 / 60)
        board.draw()

        window.listen()
        block = board.blocks[-1]
        window.onkey(block.rotate, "Up")
        window.onkey(quit_game, "q")
        window.onkey(block.move_left, "Left")
        window.onkey(block.move_right, "Right")

        if board.game_over:
            for block in board.blocks:
                if block.moving:
                    block.moving = False

            lose_turtle.goto(-520, -200)
            lose_turtle.pencolor("red")
            text = '''
                GAME OVER!
                    Score: {}
                Press q to quit
            '''.format(score)
            lose_turtle.write(text, font=("Arial", 50, "bold"))

        if not board.game_over:
            now = time.time()
            if now - start >= wait_time:
                block.move_down()
            start = time.time()

        window.update()


def play():
    window.clear()
    main()


def quit_game():
    window.clear()
    menu()


def menu():
    play_turtle = turtle.Turtle()
    play_turtle.ht()
    play_turtle.speed(0)
    play_turtle.penup()
    play_turtle.pencolor("white")

    text_turtle.pencolor("white")
    window.bgpic("tetris_bg.gif")

    text_turtle.goto(-195, 160)
    text_turtle.write("TETRIS", font=("comicsans", 80, "bold"))

    play_turtle.goto(-225, -100)
    play_turtle.write("Press any key\n     to play", font=("Arial", 50, "bold"))

    window.listen()
    window.onkeypress(play)

    window.mainloop()


if __name__ == "__main__":
    menu()
