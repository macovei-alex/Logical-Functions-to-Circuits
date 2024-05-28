from sympy import simplify
from math import log
import tkinter
from GATE_class import GATE


# creearea ferestrei principale
def create_window():
    WIDTH, HEIGHT = 1600, 800
    window = tkinter.Tk()
    # window.attributes('-fullscreen', True)
    window.title("Circuit")
    # close_button = tkinter.Button(window, width=8, height=2, background="red", command=window.destroy)
    # close_button.pack(anchor='ne')
    canvas = tkinter.Canvas(master=window, width=WIDTH, height=HEIGHT, background="white")
    canvas.pack()
    return window, canvas, WIDTH, HEIGHT


# initializarea listei de porti logice cu portile implicite (ale liniilor implicite de intrare)
def setup_default_gates(var_count, starting_y_offset):
    gates = []
    for i in range(0, var_count):
        gates.append(GATE(type="NOT", x=100, y=starting_y_offset + GATE.INPUT_LINES_DISTANCE * i, inputs=[], name=chr(ord('a') + i)))
        gates.append(GATE(type="NOT", x=100, y=starting_y_offset + GATE.INPUT_LINES_DISTANCE // 2 + GATE.INPUT_LINES_DISTANCE * i, inputs=[], name='~' + chr(ord('a') + i)))
    return gates


# desenarea partii superioare a circuitului
def setup_canvas(var_count, width):
    starting_y_offset = 20
    y_offset = starting_y_offset
    while y_offset < GATE.INPUT_LINES_DISTANCE * var_count:
        GATE.CANVAS.create_line(40, y_offset, width - 20, y_offset, fill=GATE.line_color(y_offset), width=GATE.LINE_WIDTH)
        Not = GATE(type="NOT", x=100, y=y_offset + GATE.INPUT_LINES_DISTANCE // 2, inputs=[(50, y_offset)], name="")
        Not.draw()
        GATE.CANVAS.create_line(Not.x + GATE.SIZE, Not.y, width - 20, Not.y, fill=GATE.line_color(Not.y), width=GATE.LINE_WIDTH)
        GATE.CANVAS.create_text(30, y_offset, text=chr(ord("a") + y_offset // GATE.INPUT_LINES_DISTANCE), font=1)
        GATE.CANVAS.create_text(24, y_offset + GATE.INPUT_LINES_DISTANCE // 2, text="~" + chr(ord("a") + y_offset // GATE.INPUT_LINES_DISTANCE), font=1)
        y_offset += GATE.INPUT_LINES_DISTANCE
    return setup_default_gates(var_count, starting_y_offset)


# construirea si simplificarea expresiei logice dintr-un tabel de valori
def expr_from_table(file_name):
    lines = open(file_name, "r").read().split("\n")
    expr = ""
    var_count = len(lines[0]) // 2

    for i in range(1, len(lines)):
        func_values = [int(x) for x in lines[i].split(" ")]
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
def expr_from_line(file_name):
    file = open(file_name, "r")
    values = [int(x) for x in file.readline() if x.isdigit()]
    var_count = int(log(len(values), 2))
    expr = ""

    for i in range(0, len(values)):
        if values[i] == 1:
            expr += " | "
            min_term = ""
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


def list_sum(ls, start, stop):
    suma = 0
    for i in range(start, stop):
        suma += ls[i]
    return suma


def is_operator(character):
    return character in ['&', '|', '~']


def priority(operator):
    if operator == '~':
        return 2
    elif operator == '&' or operator == '|':
        return 1
    else:
        return 0


def reverse_polish_notation(expr):
    expr = expr.replace('(', ' ( ')
    expr = expr.replace(')', ' ) ')
    expr = expr.replace('&', ' & ')
    expr = expr.replace('|', ' | ')
    expr = expr.replace('~', ' ~ ')
    expr = expr.split()

    output = []
    stack = []

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


def new_gate(gates, left_term, right_term, operator):

    # cautarea portilor de intrare dupa nume
    input_1 = GATE("", 0, 0, [])
    input_2 = GATE("", 0, 0, [])
    for gate in gates:
        if gate.name == left_term:
            input_1 = gate
        if gate.name == right_term:
            input_2 = gate

    # determinarea tipului portii
    gate_type = ""
    if operator == '&':
        gate_type = "AND"
    elif operator == '|':
        gate_type = "OR"

    # initializarea portilor logice in functie de expresiile lor
    gates.append(GATE(
        type = gate_type,
        inputs = [(input_1.x, input_1.y), (input_2.x, input_2.y)],
        input_names = [left_term, right_term],
        name = left_term + operator + right_term,
        level = 1 + max(input_1.level, input_2.level)))


def determine_inputs(gates, gate):

    # se cauta portile logice cu liniile de intrare dupa expresia lor logica
    input_1 = GATE("", 0, 0, [])
    input_2 = GATE("", 0, 0, [])
    for input_gate in gates:
        if input_gate.name == gate.input_names[0]:
            input_1 = input_gate
        if input_gate.name == gate.input_names[1]:
            input_2 = input_gate

    # verificarea cazului in care intrarile sunt de pe liniile intrarilor implicite si calcularea coordonatelor de punctelor de intrare (difera de ale porile de intrare)
    if input_1.level == 0:
        gate.inputs[0] = (gate.x - gate.level_width + gate.x_offset + GATE.SIZE, input_1.y)
    else:
        gate.inputs[0] = (input_1.x + GATE.SIZE, input_1.y)

    if input_2.level == 0:
        gate.inputs[1] = (gate.x - gate.level_width + gate.x_offset + GATE.SIZE, input_2.y)
    else:
        gate.inputs[1] = (input_2.x + GATE.SIZE, input_2.y)

    # sortarea intrarilor dupa coordonata y
    if gate.inputs[0][1] > gate.inputs[1][1]:
        gate.inputs = [(gate.inputs[1][0], gate.inputs[1][1]), (gate.inputs[0][0], gate.inputs[0][1])]

    return gate


def find_gate(gates, name):
    for gate in gates:
        if gate.name == name:
            return gate


def count_gates_per_level(gates, level):
    counter = 0
    for gate in gates:
        if gate.level > level:
            return counter
        if gate.level == level:
            counter += 1
    return counter


def height_adjustment(gates, i, gate_y):
    height_changed = True
    while height_changed is True:
        height_changed = False
        for higher_level_gate in gates:
            if higher_level_gate.level > gates[i].level:
                input_gate_1 = find_gate(gates, higher_level_gate.input_names[0])
                input_gate_2 = find_gate(gates, higher_level_gate.input_names[1])
                if (input_gate_1.y == gate_y and input_gate_1.level < gates[i].level) or (input_gate_2.y == gate_y and input_gate_2.level < gates[i].level):
                    gate_y += 3 * GATE.SIZE
                    height_changed = True
                if (input_gate_1.y == gate_y and input_gate_1.level < gates[i].level) or (input_gate_2.y == gate_y and input_gate_2.level < gates[i].level):
                    gate_y += 3 * GATE.SIZE
                    height_changed = True
    return gate_y


def build_gates(expr, gates):

    # prelucrarea formei poloneze postfixate pentru a initializa expresiile portilor
    i = 0
    while i < len(expr):
        if is_operator(expr[i]) is True:
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
    gates = sorted(gates, key=lambda gate: gate.level)
    level_width = [0]
    for level in range(1, gates[len(gates) - 1].level + 1):
        level_width.append(3 * GATE.SIZE + 3 * GATE.INPUTS_X_OFFSET * count_gates_per_level(gates, level))

    # determinarea pozitiei geometrice a portilor si a intrarilor in porti
    # coordonatele x pleaca de la 120 pentru a putea trage linii de la intrarile implicite fara a desena peste portile NOT
    gate_x = 120
    id = 1
    for level in range(1, gates[len(gates) - 1].level + 1):
        gate_y = GATE.Y_MIN
        gate_x += level_width[level]

        # distanta pe Ox fata de poarta logica asociata unde se face "cotitura" liniei de intrare
        gate_x_offset = 3 * GATE.INPUTS_X_OFFSET

        for i in range(0, len(gates)):
            if gates[i].level > level:
                break

            if gates[i].level == level:
                gates[i].x = gate_x
                gates[i].x_offset = gate_x_offset
                gate_y = height_adjustment(gates, i, gate_y)
                gates[i].y = gate_y
                gates[i].level_width = level_width[level]
                gates[i].id = id

                gate_x_offset += 3 * GATE.INPUTS_X_OFFSET
                gate_y += 3 * GATE.SIZE
                id += 1

                # determinarea coordonatelor liniilor de intrare in poarta
                gates[i] = determine_inputs(gates, gates[i])

    return gates
