import tkinter
from math import log

from sympy import simplify

from Gate import Gate


# creearea ferestrei principale
def create_window():
    WIDTH, HEIGHT = 1600, 800
    window = tkinter.Tk()
    window.title("Circuit")
    canvas = tkinter.Canvas(master=window, width=WIDTH, height=HEIGHT, background="white")
    canvas.pack()
    return window, canvas, WIDTH, HEIGHT


# initializarea listei de porti logice cu portile implicite (ale liniilor implicite de intrare)
def setup_default_gates(var_count: int, starting_y_offset: int) -> list[Gate]:
    gates: list[Gate] = []
    for i in range(0, var_count):
        gates.append(Gate(gate_type="NOT", x=100,
                          y=starting_y_offset + Gate.INPUT_LINES_DISTANCE * i,
                          inputs=[], name=chr(ord('a') + i)))
        gates.append(Gate(gate_type="NOT", x=100,
                          y=starting_y_offset + Gate.INPUT_LINES_DISTANCE // 2 + Gate.INPUT_LINES_DISTANCE * i,
                          inputs=[], name='~' + chr(ord('a') + i)))
    return gates


# desenarea partii superioare a circuitului
def setup_canvas(canvas: tkinter.Canvas, var_count: int, width: int) -> list[Gate]:
    starting_y_offset: int = 20
    y_offset: int = starting_y_offset
    while y_offset < Gate.INPUT_LINES_DISTANCE * var_count:
        canvas.create_line(40, y_offset, width - 20, y_offset,
                           fill=Gate.line_color(y_offset), width=Gate.LINE_WIDTH)
        not_gate: Gate = Gate(
            gate_type="NOT", x=100,
            y=y_offset + Gate.INPUT_LINES_DISTANCE // 2,
            inputs=[(50, y_offset)], name="")
        not_gate.draw(canvas)

        canvas.create_line(not_gate.x + Gate.SIZE, not_gate.y, width - 20, not_gate.y,
                           fill=Gate.line_color(not_gate.y), width=Gate.LINE_WIDTH)
        canvas.create_text(30, y_offset,
                           text=chr(ord("a") + y_offset // Gate.INPUT_LINES_DISTANCE), font=1)
        canvas.create_text(24, y_offset + Gate.INPUT_LINES_DISTANCE // 2,
                           text="~" + chr(ord("a") + y_offset // Gate.INPUT_LINES_DISTANCE), font=1)

        y_offset += Gate.INPUT_LINES_DISTANCE

    return setup_default_gates(var_count, starting_y_offset)


# construirea si simplificarea expresiei logice dintr-un tabel de valori
def expr_from_table(file_name: str) -> tuple[str, int]:
    with open(file_name, "r") as file:
        lines: list[str] = file.read().split("\n")
    expr: str = ""
    var_count: int = len(lines[0]) // 2

    for i in range(1, len(lines)):
        func_values: list[int] = [int(x) for x in lines[i].split(" ")]
        if func_values[var_count] == 1:
            expr += " | "
            for j in range(0, var_count):
                if func_values[j] == 0:
                    expr += "~"
                expr += chr(ord('a') + j) + "&"
            expr = expr[:-1]
    if expr == "":
        return "False", var_count
    else:
        expr = expr[3:]
        expr = repr(simplify(expr)).replace(" ", "")
        return expr, var_count


# construirea si simplificarea expresiei logice dintr-un fisier ce contine valorile functiei logice in ordine (valorile din tabel citite de sus in jos) pe o linie
def expr_from_line(file_name: str) -> tuple[str, int]:
    with open(file_name, "r") as file:
        lines: list[str] = file.read().split(" ")
    values: list[int] = [int(x) for x in lines if x.isdigit()]
    var_count: int = int(log(len(values), 2))
    expr: str = ""

    for i in range(0, len(values)):
        if values[i] == 1:
            expr += " | "
            min_term: str = ""
            for rank in range(0, var_count):
                min_term += chr(ord('a') + var_count - rank - 1)
                if i % 2 == 0:
                    min_term += "~"
                min_term += "&"
                i //= 2
            min_term = min_term[:-1][::-1]
            expr += min_term
    if expr == "":
        return "False", var_count
    else:
        expr = expr[3:]
        expr = repr(simplify(expr)).replace(" ", "")
        return expr, var_count


def is_operator(character: str) -> bool:
    return character in ['&', '|', '~']


def priority(operator: str) -> int:
    if operator == '~':
        return 2
    elif operator == '&' or operator == '|':
        return 1
    else:
        return 0


def reverse_polish_notation(expr: str) -> list[str]:
    expr = expr.replace('(', ' ( ')
    expr = expr.replace(')', ' ) ')
    expr = expr.replace('&', ' & ')
    expr = expr.replace('|', ' | ')
    expr = expr.replace('~', ' ~ ')
    expr = expr.split()

    output: list[str] = []
    stack: list[str] = []

    for character in expr:
        if character.isalpha():
            output.append(character)
        elif is_operator(character):
            while stack and is_operator(stack[-1]) and priority(stack[-1]) >= priority(character):
                output.append(stack.pop())
            stack.append(character)
        elif character == '(':
            stack.append(character)
        elif character == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()

    while stack:
        output.append(stack.pop())
    return output


def new_gate(gates: list[Gate], left_term: str, right_term: str, operator: str) -> None:
    input_1: Gate | None = None
    input_2: Gate | None = None
    for gate in gates:
        if gate.name == left_term:
            input_1 = gate
        if gate.name == right_term:
            input_2 = gate

    # determinarea tipului portii
    gate_type: str = ""
    if operator == '&':
        gate_type = "AND"
    elif operator == '|':
        gate_type = "OR"

    # initializarea portilor logice in functie de expresiile lor
    gates.append(Gate(
        gate_type=gate_type,
        inputs=[(input_1.x, input_1.y), (input_2.x, input_2.y)],
        input_names=[left_term, right_term],
        name=left_term + operator + right_term,
        level=1 + max(input_1.level, input_2.level)))


def determine_inputs(gates: list[Gate], gate: Gate) -> None:
    # se cauta portile logice cu liniile de intrare dupa expresia lor logica
    input_1: Gate | None = None
    input_2: Gate | None = None
    for input_gate in gates:
        if input_gate.name == gate.input_names[0]:
            input_1 = input_gate
        if input_gate.name == gate.input_names[1]:
            input_2 = input_gate

    # verificarea cazului in care intrarile sunt de pe liniile intrarilor implicite si calcularea coordonatelor de punctelor de intrare (difera de ale porile de intrare)
    if input_1.level == 0:
        gate.inputs[0] = (gate.x - gate.level_width + gate.x_offset + Gate.SIZE, input_1.y)
    else:
        gate.inputs[0] = (input_1.x + Gate.SIZE, input_1.y)

    if input_2.level == 0:
        gate.inputs[1] = (gate.x - gate.level_width + gate.x_offset + Gate.SIZE, input_2.y)
    else:
        gate.inputs[1] = (input_2.x + Gate.SIZE, input_2.y)

    # sortarea intrarilor dupa coordonata y
    if gate.inputs[0][1] > gate.inputs[1][1]:
        gate.inputs = [(gate.inputs[1][0], gate.inputs[1][1]), (gate.inputs[0][0], gate.inputs[0][1])]


def find_gate(gates: list[Gate], name: str) -> Gate | None:
    for gate in gates:
        if gate.name == name:
            return gate
    return None


def count_gates_per_level(gates: list[Gate], level: int) -> int:
    counter: int = 0
    for gate in gates:
        if gate.level > level:
            return counter
        if gate.level == level:
            counter += 1
    return counter


def height_adjustment(gates: list[Gate], i: int, gate_y: int) -> int:
    height_changed: bool = True
    while height_changed is True:
        height_changed = False
        for higher_level_gate in gates:
            if higher_level_gate.level > gates[i].level:
                input_gate_1 = find_gate(gates, higher_level_gate.input_names[0])
                input_gate_2 = find_gate(gates, higher_level_gate.input_names[1])
                if (input_gate_1.y == gate_y and input_gate_1.level < gates[i].level) or (input_gate_2.y == gate_y and input_gate_2.level < gates[i].level):
                    gate_y += 3 * Gate.SIZE
                    height_changed = True
                if (input_gate_1.y == gate_y and input_gate_1.level < gates[i].level) or (input_gate_2.y == gate_y and input_gate_2.level < gates[i].level):
                    gate_y += 3 * Gate.SIZE
                    height_changed = True
    return gate_y


def build_gates(expr: list[str], gates: list[Gate]) -> list[Gate]:
    # prelucrarea formei poloneze postfixate pentru a initializa expresiile portilor
    i: int = 0
    while i < len(expr):
        if is_operator(expr[i]):
            if expr[i] == '&' or expr[i] == '|':
                new_gate(gates, expr[i - 2], expr[i - 1], expr[i])
                expr[i - 2] = expr[i - 2] + expr[i] + expr[i - 1]
                expr.pop(i)
                expr.pop(i - 1)
                i -= 2
            elif expr[i] == '~':
                expr[i - 1] = '~' + expr[i - 1]
                expr.pop(i)
                i -= 1
        i += 1

    # lista de porti este sortata dupa nivelul pe care se afla portile
    gates: list[Gate] = sorted(gates, key=lambda gate: gate.level)
    level_width: list[int] = [0]
    for level in range(1, gates[len(gates) - 1].level + 1):
        level_width.append(3 * Gate.SIZE + 3 * Gate.INPUTS_X_OFFSET * count_gates_per_level(gates, level))

    # determinarea pozitiei geometrice a portilor si a intrarilor in porti
    # coordonatele x pleaca de la 120 pentru a putea trage linii de la intrarile implicite fara a desena peste portile NOT
    gate_x: int = 120
    gate_id: int = 1
    for level in range(1, gates[len(gates) - 1].level + 1):
        gate_y: int = Gate.Y_MIN
        gate_x += level_width[level]

        # distanta pe Ox fata de poarta logica asociata unde se face "cotitura" liniei de intrare
        gate_x_offset: int = 3 * Gate.INPUTS_X_OFFSET

        for i in range(0, len(gates)):
            if gates[i].level > level:
                break

            if gates[i].level == level:
                gates[i].x = gate_x
                gates[i].x_offset = gate_x_offset
                gate_y = height_adjustment(gates, i, gate_y)
                gates[i].y = gate_y
                gates[i].level_width = level_width[level]
                gates[i].id = gate_id

                gate_x_offset += 3 * Gate.INPUTS_X_OFFSET
                gate_y += 3 * Gate.SIZE
                gate_id += 1

                # determinarea coordonatelor liniilor de intrare in poarta
                determine_inputs(gates, gates[i])

    return gates
