import string

from functions import *

expr = ""
var_count = 0

# construirea si simplificarea expresiei logice
print("Select the input file: ")
print("  - enter 1 to input from file \"table.txt\"")
print("  - enter 2 to input from file \"line.txt\"")
input_file_nr = int(input())
if input_file_nr == 1:
    expr, var_count = expr_from_table("..\\resources\\table.txt")
elif input_file_nr == 2:
    expr, var_count = expr_from_line("..\\resources\\line.txt")
print(expr)

# verificarea ca expresia logica sa nu fie functia constanta 0 sau 1 sau o functie fara porti logice AND sau OR
if expr == "True" or expr == "False":
    print("Constant ", end="")
    if expr == "True":
        print(1, end="")
    else:
        print(0, end="")
    print(" function")
    exit(0)
elif len(expr) == 1 or len(expr) == 2:
    print("Functia este echivalenta cu valoarea variabilei de intrare: ", expr)
    exit(0)

# alcatuirea formei poloneze prefixate ale expresiei logice
rpn = reverse_polish_notation(expr)

# creearea ferestrei si plansei de desen
window, canvas, WIDTH, HEIGHT = create_window()

# initializarea membrilor statici ai clasei
GATE.CANVAS = canvas
GATE.Y_MIN = 20 + 40 * var_count + 2 * GATE.SIZE

# initializarea listei de porti cu intrarile implicite (ex: a si ~a), care sunt tratate ca porti logice, si desenarea intrarilor implicite
gates = setup_canvas(var_count, WIDTH)

# construirea listei de porti logice cu specifice
gates = build_gates(rpn, gates)

# desenarea pe plansa si afisarea unor caracteristici ale portilor logice in consola
for i in range(2 * var_count, len(gates)):
    gates[i].draw()
    print("Poarta nr.", i - 2 * var_count + 1, gates[i].level, gates[i].input_names[0], gates[i].type, gates[i].input_names[1])

# pastrarea deschisa a ferestrei
window.mainloop()
