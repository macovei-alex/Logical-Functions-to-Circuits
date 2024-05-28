import tkinter

# fereastra care ajuta la initializarea variabilei CANVAS
root = tkinter.Tk()
root.withdraw()


class GATE:

    # marimea unei porti logice
    SIZE = 20

    # exista pentru a nu se mai transmite ca parametru de fiecare data plansa de desen
    # variabila initializata cu o plansa a unei alte ferestre decat cea de desen, fereastra care nu se deschide
    CANVAS = tkinter.Canvas(root)

    # offsetul dintre cele 2 intrari ale unei porti
    INPUTS_X_OFFSET = 8

    # inaltimea de la care se incepe desenarea portilor pentru fiecare nivel (banda)
    Y_MIN = 0

    # grosimea liniilor
    LINE_WIDTH = 2

    # distanta dintre 2 intrari ne-negate
    INPUT_LINES_DISTANCE = 40

    # culorile liniilor de intrare
    LINE_COLOR = ['#cf0404', '#de4949', '#f59700', '#f7b954', '#c7c416', '#fffb03', '#5ee305', '#a1f569', '#0254bf', '#6faaf7', '#9005a8', '#e884fa']

    def __init__(self, type, inputs, level_width=0, x=0, y=0, input_names=list[""], name="", level=0, id=0):

        # poate fi "NOT", "AND" sau "OR" pentru ca poarta sa fie valida
        self.type = type

        # coordonatele "centrului" portii
        # poarta se deseneaza in raport cu un patrat cu centrul in (x, y) si lungimea laturii 2 * SIZE
        self.x = x
        self.y = y

        # coordonatele punctelor ce reprezinta portile de input (difera de coordonatelor portilor de input)
        self.inputs = inputs

        # expresiile portilor de input
        self.input_names = input_names

        # expresia pe care poarta o reprezinta
        self.name = name

        # nivelul pe care se afla poarta logica
        self.level = level

        # diferenta in coordonata x dintre primele linii de input ale 2 porti consecutive
        self.x_offset = 0

        # latimea nivelului pe care se afla poarta curenta
        self.level_width = level_width

        self.id = id

    def draw(self):
        if self.type == "AND":
            self.draw_and()
        elif self.type == "OR":
            self.draw_or()
        elif self.type == "NOT":
            self.draw_not()
        else:
            print("Invalid gate type")
            return
        self.draw_inputs()

    def draw_and(self):
        x = self.x
        y = self.y
        size = self.SIZE
        self.CANVAS.create_line(x - size, y - size, x, y - size, width=GATE.LINE_WIDTH)
        self.CANVAS.create_line(x - size, y + size, x, y + size, width=GATE.LINE_WIDTH)
        self.CANVAS.create_line(x - size, y - size, x - size, y + size, width=GATE.LINE_WIDTH)
        self.CANVAS.create_arc(x - size, y - size, x + size, y + size, style="arc", start=-90, extent=180, width=GATE.LINE_WIDTH)
        self.CANVAS.create_text(self.x, self.y, text=self.id)

    def draw_or(self):
        x = self.x
        y = self.y
        size = self.SIZE
        self.CANVAS.create_arc(x - 5.1 * size, y - 1 * size, x + 1.9 * size, y + 5 * size, style="arc", start=41, extent=45, width=GATE.LINE_WIDTH)
        self.CANVAS.create_arc(x - 5.1 * size, y + 1 * size, x + 1.9 * size, y - 5 * size, style="arc", start=-41, extent=-45, width=GATE.LINE_WIDTH)
        self.CANVAS.create_arc(x - 4 * size, y - 1.5 * size, x - size, y + 1.5 * size, style="arc", start=-42, extent=84, width=GATE.LINE_WIDTH)
        self.CANVAS.create_text(self.x, self.y, text=self.id)

    def draw_not(self):
        x = self.x
        y = self.y
        size = self.SIZE
        self.CANVAS.create_polygon(x - size, y - 0.5 * size, x + 0.7 * size, y, x - size, y + 0.5 * size, fill="", outline="black", width=GATE.LINE_WIDTH)
        self.CANVAS.create_oval(x + 0.7 * size, y - 0.15 * size, x + 1 * size, y + 0.15 * size, width=GATE.LINE_WIDTH)

    def draw_inputs(self):

        #  portile NOT pot sa aiba 0 sau 1 parametru si ajuta la initializarea listei de porti logice, respectiv in reprezentarea grafica partii superioare a circuitului
        #  ele urmeaza formule diferite pentru ca sunt declarate in circumstante diferite de portile AND si OR

        if len(self.inputs) == 0 or len(self.inputs) == 1:
            color = GATE.line_color(self.inputs[0][1])
            self.CANVAS.create_line(self.inputs[0][0], self.inputs[0][1], self.x - 2 * self.SIZE, self.inputs[0][1], fill=color, width=GATE.LINE_WIDTH)
            self.CANVAS.create_line(self.x - 2 * self.SIZE, self.inputs[0][1], self.x - 2 * self.SIZE, self.y, fill=color, width=GATE.LINE_WIDTH)
            self.CANVAS.create_line(self.x - 2 * self.SIZE, self.y, self.x - self.SIZE, self.y, fill=color, width=GATE.LINE_WIDTH)

            self.CANVAS.create_oval(self.x - 2 * self.SIZE - 3, self.inputs[0][1] - 3, self.x - 2 * self.SIZE + 3, self.inputs[0][1] + 3, fill="black")

        elif len(self.inputs) == 2:

            # variabila folosita la potrivirea liniilor de input la intrarea in poarta
            partition = 2 * self.SIZE / 3

            # variabile pentru evitarea desenarii intrarilor una peste cealalta
            first_x_offset = self.x_offset + GATE.SIZE
            second_x_offset = self.x_offset + GATE.SIZE
            if self.inputs[0][1] < self.y - partition and self.inputs[1][1] < self.y + partition:
                first_x_offset += self.INPUTS_X_OFFSET
            elif self.inputs[0][1] > self.y - partition and self.inputs[1][1] > self.y + partition:
                second_x_offset += self.INPUTS_X_OFFSET

            # prima linie de intrare
            color = "black"
            if self.inputs[0][1] < GATE.Y_MIN:
                color = GATE.line_color(self.inputs[0][1])
            self.CANVAS.create_line(self.inputs[0][0], self.inputs[0][1], self.x - self.level_width + first_x_offset, self.inputs[0][1], fill=color, width=GATE.LINE_WIDTH)
            self.CANVAS.create_line(self.x - self.level_width + first_x_offset, self.inputs[0][1], self.x - self.level_width + first_x_offset, self.y - partition, fill=color, width=GATE.LINE_WIDTH)
            self.CANVAS.create_line(self.x - self.level_width + first_x_offset, self.y - partition, self.x - self.SIZE, self.y - partition, fill=color, width=GATE.LINE_WIDTH)

            # a doua linie de intrare
            color = "black"
            if self.inputs[1][1] < GATE.Y_MIN:
                color = GATE.line_color(self.inputs[1][1])
            self.CANVAS.create_line(self.inputs[1][0], self.inputs[1][1], self.x - self.level_width + second_x_offset, self.inputs[1][1], fill=color, width=GATE.LINE_WIDTH)
            self.CANVAS.create_line(self.x - self.level_width + second_x_offset, self.inputs[1][1], self.x - self.level_width + second_x_offset, self.y + partition, fill=color, width=GATE.LINE_WIDTH)
            self.CANVAS.create_line(self.x - self.level_width + second_x_offset, self.y + partition, self.x - self.SIZE, self.y + partition, fill=color, width=GATE.LINE_WIDTH)

            # desenarea punctelor de bifurcatie din liniile de intrare implicite
            if self.inputs[0][1] < GATE.Y_MIN:
                self.CANVAS.create_oval(self.x - self.level_width + first_x_offset - 3, self.inputs[0][1] - 3, self.x - self.level_width + first_x_offset + 3, self.inputs[0][1] + 3, fill="black")
            if self.inputs[1][1] < GATE.Y_MIN:
                self.CANVAS.create_oval(self.x - self.level_width + second_x_offset - 3, self.inputs[1][1] - 3, self.x - self.level_width + second_x_offset + 3, self.inputs[1][1] + 3, fill="black")

    @staticmethod
    def line_color(y_offset):
        return GATE.LINE_COLOR[(y_offset - 20) // (GATE.INPUT_LINES_DISTANCE // 2)]