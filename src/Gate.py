import tkinter


class Gate:
    # marimea unei porti logice
    SIZE: int = 20

    # offsetul dintre cele 2 intrari ale unei porti
    INPUTS_X_OFFSET: int = 8

    # inaltimea de la care se incepe desenarea portilor pentru fiecare nivel (banda)
    Y_MIN: int = 0

    # grosimea liniilor
    LINE_WIDTH: int = 2

    # distanta dintre 2 intrari ne-negate
    INPUT_LINES_DISTANCE: int = 40

    # culorile liniilor de intrare
    LINE_COLOR: list[str] = ['#cf0404', '#de4949', '#f59700', '#f7b954', '#c7c416', '#fffb03', '#5ee305', '#a1f569', '#0254bf', '#6faaf7', '#9005a8', '#e884fa']

    def __init__(self, gate_type: str, inputs: list[tuple[int, int]],
                 x: int = 0, y: int = 0,
                 id_gate: int = 0, level: int = 0, level_width: int = 0,
                 input_names: list[str] = None, name: str = ""):

        # poate fi "NOT", "AND" sau "OR" pentru ca poarta sa fie valida
        self.type: str = gate_type

        # coordonatele "centrului" portii
        # poarta se deseneaza in raport cu un patrat cu centrul in (x, y) si lungimea laturii 2 * SIZE
        self.x: int = x
        self.y: int = y

        # coordonatele punctelor ce reprezinta portile de input (difera de coordonatelor portilor de input)
        self.inputs: list[tuple[int, int]] = inputs

        # expresiile portilor de input
        self.input_names: list[str] = input_names

        # expresia pe care poarta o reprezinta
        self.name: str = name

        # nivelul pe care se afla poarta logica
        self.level: int = level

        # diferenta in coordonata x dintre primele linii de input ale 2 porti consecutive
        self.x_offset: int = 0

        # latimea nivelului pe care se afla poarta curenta
        self.level_width: int = level_width

        self.id: int = id_gate

    def draw(self, canvas: tkinter.Canvas) -> None:
        if self.type == "AND":
            self.draw_and(canvas)
        elif self.type == "OR":
            self.draw_or(canvas)
        elif self.type == "NOT":
            self.draw_not(canvas)
        else:
            print("Invalid gate type")
            return
        self.draw_inputs(canvas)

    def draw_and(self, canvas: tkinter.Canvas) -> None:
        x: int = self.x
        y: int = self.y
        size: int = Gate.SIZE

        canvas.create_line(x - size, y - size, x, y - size, width=Gate.LINE_WIDTH)
        canvas.create_line(x - size, y + size, x, y + size, width=Gate.LINE_WIDTH)
        canvas.create_line(x - size, y - size, x - size, y + size, width=Gate.LINE_WIDTH)
        canvas.create_arc(x - size, y - size, x + size, y + size, style="arc", start=-90, extent=180, width=Gate.LINE_WIDTH)
        canvas.create_text(x, y, text=self.id)

    def draw_or(self, canvas: tkinter.Canvas) -> None:
        x: int = self.x
        y: int = self.y
        size: int = Gate.SIZE

        canvas.create_arc(x - 5.1 * size, y - 1 * size, x + 1.9 * size, y + 5 * size, style="arc", start=41, extent=45, width=Gate.LINE_WIDTH)
        canvas.create_arc(x - 5.1 * size, y + 1 * size, x + 1.9 * size, y - 5 * size, style="arc", start=-41, extent=-45, width=Gate.LINE_WIDTH)
        canvas.create_arc(x - 4 * size, y - 1.5 * size, x - size, y + 1.5 * size, style="arc", start=-42, extent=84, width=Gate.LINE_WIDTH)
        canvas.create_text(x, y, text=self.id)

    def draw_not(self, canvas: tkinter.Canvas) -> None:
        x: int = self.x
        y: int = self.y
        size: int = Gate.SIZE

        canvas.create_polygon(x - size, y - 0.5 * size, x + 0.7 * size, y, x - size, y + 0.5 * size, fill="", outline="black", width=Gate.LINE_WIDTH)
        canvas.create_oval(x + 0.7 * size, y - 0.15 * size, x + 1 * size, y + 0.15 * size, width=Gate.LINE_WIDTH)

    def draw_inputs(self, canvas: tkinter.Canvas) -> None:
        #  portile NOT pot sa aiba 0 sau 1 parametru si ajuta la initializarea listei de porti logice, respectiv in reprezentarea grafica partii superioare a circuitului
        #  ele urmeaza formule diferite pentru ca sunt declarate in circumstante diferite de portile AND si OR

        x: int = self.x
        y: int = self.y
        size: int = Gate.SIZE

        if len(self.inputs) == 0 or len(self.inputs) == 1:
            color: str = Gate.line_color(self.inputs[0][1])
            canvas.create_line(self.inputs[0][0], self.inputs[0][1], x - 2 * size, self.inputs[0][1], fill=color, width=Gate.LINE_WIDTH)
            canvas.create_line(x - 2 * size, self.inputs[0][1], x - 2 * size, y, fill=color, width=Gate.LINE_WIDTH)
            canvas.create_line(x - 2 * size, y, x - size, y, fill=color, width=Gate.LINE_WIDTH)

            canvas.create_oval(x - 2 * size - 3, self.inputs[0][1] - 3, x - 2 * size + 3, self.inputs[0][1] + 3, fill="black")

        elif len(self.inputs) == 2:
            # variabila folosita la potrivirea liniilor de input la intrarea in poarta
            partition: float = 2 * size / 3

            # variabile pentru evitarea desenarii intrarilor una peste cealalta
            first_x_offset = self.x_offset + size
            second_x_offset = self.x_offset + size
            if self.inputs[0][1] < y - partition and self.inputs[1][1] < y + partition:
                first_x_offset += self.INPUTS_X_OFFSET
            elif self.inputs[0][1] > y - partition and self.inputs[1][1] > y + partition:
                second_x_offset += self.INPUTS_X_OFFSET

            # prima linie de intrare
            color: str = Gate.line_color(self.inputs[0][1]) if self.inputs[0][1] < Gate.Y_MIN else "black"
            canvas.create_line(self.inputs[0][0], self.inputs[0][1], x - self.level_width + first_x_offset, self.inputs[0][1], fill=color, width=Gate.LINE_WIDTH)
            canvas.create_line(x - self.level_width + first_x_offset, self.inputs[0][1], x - self.level_width + first_x_offset, y - partition, fill=color, width=Gate.LINE_WIDTH)
            canvas.create_line(x - self.level_width + first_x_offset, y - partition, x - size, y - partition, fill=color, width=Gate.LINE_WIDTH)

            # a doua linie de intrare
            color = Gate.line_color(self.inputs[1][1]) if self.inputs[1][1] < Gate.Y_MIN else "black"
            canvas.create_line(self.inputs[1][0], self.inputs[1][1], x - self.level_width + second_x_offset, self.inputs[1][1], fill=color, width=Gate.LINE_WIDTH)
            canvas.create_line(x - self.level_width + second_x_offset, self.inputs[1][1], x - self.level_width + second_x_offset, y + partition, fill=color, width=Gate.LINE_WIDTH)
            canvas.create_line(x - self.level_width + second_x_offset, y + partition, x - size, y + partition, fill=color, width=Gate.LINE_WIDTH)

            # desenarea punctelor de bifurcatie din liniile de intrare implicite
            if self.inputs[0][1] < Gate.Y_MIN:
                canvas.create_oval(x - self.level_width + first_x_offset - 3, self.inputs[0][1] - 3, x - self.level_width + first_x_offset + 3, self.inputs[0][1] + 3, fill="black")
            if self.inputs[1][1] < Gate.Y_MIN:
                canvas.create_oval(x - self.level_width + second_x_offset - 3, self.inputs[1][1] - 3, x - self.level_width + second_x_offset + 3, self.inputs[1][1] + 3, fill="black")

    @staticmethod
    def line_color(y_offset) -> str:
        return Gate.LINE_COLOR[(y_offset - 20) // (Gate.INPUT_LINES_DISTANCE // 2)]
