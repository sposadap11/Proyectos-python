import random

print("¡Bienvenido a la adivinanza!")
print("Estoy pensando en un número del 1 al 100.")
print("Intenta adivinar cuál es ese número.")

numero_secreto = random.randint(1, 100)
intentos = 0

while True:
    intentos += 1
    intento = int(input("Ingresa tu intento: "))
    
    if intento == numero_secreto:
        print("¡Felicidades! Adivinaste el número en", intentos, "intentos.")
        break
    elif intento < numero_secreto:
        print("Fallaste. El número es mayor que", intento)
    else:
        print("Fallaste. El número es menor que", intento)
