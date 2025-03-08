import turtle
import random

screen = turtle.Screen()
screen.bgcolor("lightblue")
screen.title("Букет роз")
screen.setup(width=500, height=500)

t = turtle.Turtle()
t.speed(-1)
t.width(3)

def draw_rose_bud(x, y, color, angle):
    t.penup()
    t.goto(x, y)
    t.setheading(angle)
    t.pendown()
    t.color(color)
    t.begin_fill()
    t.circle(20, 180)
    t.circle(40, 180)
    t.end_fill()

def draw_stem(x, y, length, angle):
    t.penup()
    t.goto(x, y)
    t.setheading(90 + angle)
    t.pendown()
    t.color("green")
    t.forward(length)
    return t.pos()

def draw_flower(x, y, bud_color, stem_length, stem_angle):
    end_of_stem = draw_stem(x, y, stem_length, stem_angle)
    draw_rose_bud(end_of_stem[0], end_of_stem[1], bud_color, 90 + stem_angle)

def draw_bow(x, y, color):
    t.penup()
    t.goto(x, y)
    t.pendown()
    t.color(color)
    t.begin_fill()
    t.left(45)
    t.forward(50)
    t.right(90)
    t.forward(40)
    t.right(90)
    t.forward(40)
    t.right(90)
    t.forward(40)
    t.end_fill()
    t.begin_fill()
    t.right(135)
    t.forward(40)
    t.left(90)
    t.forward(40)
    t.left(90)
    t.forward(40)
    t.left(90)
    t.forward(40)
    t.end_fill()

def write_text(x, y, text):
    t.penup()
    t.goto(x, y)
    t.pendown()
    t.color("black")
    t.write(text, align="center", font=("Arial", 36, "bold"))

num_flowers = 9
base_x, base_y = 0, -100

for _ in range(num_flowers):
    bud_color = random.choice(["red", "pink", "magenta", "purple"])
    stem_length = random.randint(150, 200)
    stem_angle = random.randint(-20, 20)
    draw_flower(base_x, base_y, bud_color, stem_length, stem_angle)

bow_color = random.choice(["red", "blue", "yellow", "orange"])
draw_bow( 15, base_y + 20, bow_color)

write_text(base_x, base_y + 250, "С 8 марта!")

t.hideturtle()
screen.mainloop()