import random
import tkinter as tk
from tkinter import messagebox

# Función para verificar el intento del jugador
def verificar_intentos():
    global intentos_restantes
    intento = None
    try:
        intento = int(entry_intentos.get())
    except ValueError:
        messagebox.showerror("Error", "Por favor ingresa un número válido.")
    if intento:
        if intento == numero_secreto:
            messagebox.showinfo("¡Felicidades!", "¡Adivinaste el número en {} intentos!".format(intentos_restantes))
            reiniciar_juego()
        elif intento < numero_secreto:
            messagebox.showinfo("Fallaste", "El número es mayor que {}".format(intento))
            intentos_restantes -= 1
        else:
            messagebox.showinfo("Fallaste", "El número es menor que {}".format(intento))
            intentos_restantes -= 1
        if intentos_restantes == 0:
            messagebox.showinfo("Derrota", "¡Te quedaste sin intentos! El número secreto era: {}".format(numero_secreto))
            reiniciar_juego()
        else:
            label_intentos.config(text="Intentos restantes: {}".format(intentos_restantes))

# Función para reiniciar el juego
def reiniciar_juego():
    global numero_secreto, intentos_restantes
    numero_secreto = random.randint(1, 100)
    intentos_restantes = 5
    label_intentos.config(text="Intentos restantes: {}".format(intentos_restantes))
    entry_intentos.delete(0, tk.END)

# Crear ventana principal
root = tk.Tk()
root.title("Adivinanza")
root.geometry("300x200")

# Variables globales
numero_secreto = random.randint(1, 100)
intentos_restantes = 5

# Crear widgets
label_instrucciones = tk.Label(root, text="Estoy pensando en un número del 1 al 100. Intenta adivinar cuál es ese número.")
label_instrucciones.pack(pady=10)

entry_intentos = tk.Entry(root)
entry_intentos.pack(pady=10)

btn_verificar = tk.Button(root, text="Verificar", command=verificar_intentos)
btn_verificar.pack()

label_intentos = tk.Label(root, text="Intentos restantes: {}".format(intentos_restantes))
label_intentos.pack()

btn_reiniciar = tk.Button(root, text="Reiniciar", command=reiniciar_juego)
btn_reiniciar.pack()

# Iniciar bucle de eventos
root.mainloop()