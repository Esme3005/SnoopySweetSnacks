import tkinter as tk
from PIL import Image, ImageTk
import random
import threading
import time
import os

# ============================================================
# CONFIGURACIÓN DEL JUEGO
# ============================================================
WIDTH, HEIGHT = 700, 500  # Dimensiones de la ventana
MAX_MISSES = 5  # Máximo de frutas que pueden pasar (vidas)
MAX_FOODS = 4 # Máximo de frutas simultáneas en pantalla

# Velocidad base de caída de frutas
FOOD_SPEED_BASE = 5
FOOD_SPEED_MAX = 400 # Velocidad máxima cuando sube la dificultad

# Intervalo de generación de frutas
SPAWN_INTERVAL_BASE = 1.0  # Cada 1 segundo
SPAWN_INTERVAL_MIN = 0.02 # Mínimo cuando sube dificultad

# Variables globales de velocidad y generación
food_speed = FOOD_SPEED_BASE
spawn_interval = SPAWN_INTERVAL_BASE

# ============================================================
# CREAR INTERFAZ TKINTER
# ============================================================
root = tk.Tk()  # Crear ventana principal
root.title("Snoopy")  # Título de la ventana

# Crear canvas (lienzo) donde se dibuja el juego
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT)
canvas.pack()

# ============================================================
# CARGAR IMÁGENES
# ============================================================
PATH = "/Users/esme/Desktop/Snoopy/SnoopySweetSnacks/"

def load_image(name, size):
    """Cargar una imagen, redimensionarla y convertirla a PhotoImage"""
    img = Image.open(os.path.join(PATH, name)).resize(size)
    return ImageTk.PhotoImage(img)

# Cargar todas las imágenes del juego
bg_tk = load_image("f1.jpg", (WIDTH, HEIGHT))  # Fondo
snoopy_tk = load_image("i1.png", (80, 80))  # Jugador (Snoopy)
cherry_tk = load_image("i2.jpeg", (40, 40))  # Cereza (restaura vida)
strawberry_tk = load_image("i3.jpeg", (40, 40))  # Fresa (suma puntos)

# Mantener referencias de las imágenes para evitar que desaparezcan
IMAGES = [bg_tk, snoopy_tk, cherry_tk, strawberry_tk]

# Dibujar fondo SOLO UNA VEZ (se mantiene durante todo el juego)
bg_item = canvas.create_image(0, 0, image=bg_tk, anchor="nw")
canvas.tag_lower(bg_item)  # Enviar el fondo atrás de otros elementos

# ============================================================
# GESTIÓN DE PUNTUACIÓN MÁXIMA
# ============================================================
HIGHSCORE_FILE = os.path.join(PATH, "highscore.txt")

def load_highscore():
    """Cargar puntuación máxima desde archivo"""
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r") as f:
                return int(f.read())
        except:
            return 0
    return 0

def save_highscore(score):
    """Guardar puntuación máxima en archivo"""
    with open(HIGHSCORE_FILE, "w") as f:
        f.write(str(score))

# Cargar puntuación máxima al iniciar
highscore = load_highscore()

# ============================================================
# VARIABLES DE JUEGO
# ============================================================
player = canvas.create_image(WIDTH//2, HEIGHT - 100, image=snoopy_tk)  # Crear jugador
foods = []  # Lista de frutas en pantalla
score = 0  # Puntuación actual
misses = 0  # Frutas que han pasado (vidas restantes)
running = True  # Controlar si el juego está en ejecución
game_over = False  # Bandera para fin de juego

# Lock para sincronización entre hilos
lock = threading.Lock()

# ============================================================
# CONTROL DE MOVIMIENTO DEL JUGADOR
# ============================================================
keys = {"left": False, "right": False}  # Estado de teclas presionadas

def key_down(event):
    """Detectar cuando se presiona una tecla"""
    if event.keysym == "Left":
        keys["left"] = True
    if event.keysym == "Right":
        keys["right"] = True

def key_up(event):
    """Detectar cuando se suelta una tecla"""
    if event.keysym == "Left":
        keys["left"] = False
    if event.keysym == "Right":
        keys["right"] = False

# Vincular eventos de teclado
root.bind("<KeyPress>", key_down)
root.bind("<KeyRelease>", key_up)

# ============================================================
# HILO 1: GENERAR FRUTAS
# ============================================================
def spawn_thread():
    """Hilo que genera frutas periódicamente"""
    global spawn_interval, running, game_over
    
    while running and not game_over:
        time.sleep(spawn_interval)  # Esperar antes de generar siguiente fruta
        
        with lock:  # Usar lock para evitar conflictos con otros hilos
            if len(foods) < MAX_FOODS and not game_over:
                # Generar fruta en posición X aleatoria
                x = random.randint(20, WIDTH - 20)

                # 20% probabilidad de ser cereza (vida), 80% fresa (puntos)
                if random.random() < 0.2:
                    img = cherry_tk
                    is_life = True
                else:
                    img = strawberry_tk
                    is_life = False

                # Crear imagen de fruta en canvas
                item = canvas.create_image(x, -20, image=img)
                # Agregar a lista de frutas con su ID y tipo
                foods.append({"id": item, "life": is_life})

# ============================================================
# HILO 2: AUMENTAR DIFICULTAD
# ============================================================
def difficulty_thread():
    """Hilo que aumenta la dificultad cada 10 puntos"""
    global food_speed, spawn_interval, score, running, game_over
    
    while running and not game_over:
        time.sleep(2)  # Revisar cada 1 segundo
        
        with lock:
            # Aumentar velocidad: 0.5 píxeles por cada 10 puntos (máximo 8)
            food_speed = min(FOOD_SPEED_BASE + (score // 10) * 3.5, FOOD_SPEED_MAX)
            
            # Disminuir intervalo de generación: 0.05s menos por cada 10 puntos
            spawn_interval = max(SPAWN_INTERVAL_MIN, SPAWN_INTERVAL_BASE - (score // 10) * 3.5)

# Iniciar ambos hilos como daemons (se cierran con el programa)
threading.Thread(target=spawn_thread, daemon=True).start()
threading.Thread(target=difficulty_thread, daemon=True).start()

# ============================================================
# FUNCIONES DE REINICIO Y GAME OVER
# ============================================================
def restart_game():
    """Reiniciar el juego completamente"""
    global score, misses, running, game_over, food_speed, spawn_interval, foods
    
    # Resetear variables
    score = 0
    misses = 0
    game_over = False
    food_speed = FOOD_SPEED_BASE
    spawn_interval = SPAWN_INTERVAL_BASE
    
    # Eliminar todas las frutas de pantalla
    with lock:
        for f in foods:
            canvas.delete(f["id"])
        foods.clear()
    
    # Limpiar canvas y redibujar fondo
    canvas.delete("all")
    bg_item = canvas.create_image(0, 0, image=bg_tk, anchor="nw")
    canvas.tag_lower(bg_item)
    
    # Recrear jugador en centro inferior
    global player
    player = canvas.create_image(WIDTH//2, HEIGHT - 100, image=snoopy_tk)
    
    # Reiniciar hilos de generación y dificultad
    threading.Thread(target=spawn_thread, daemon=True).start()
    threading.Thread(target=difficulty_thread, daemon=True).start()
    
    # Reiniciar loop principal del juego
    game_loop()

def show_game_over():
    """Mostrar pantalla de Game Over con botón de reinicio"""
    global highscore
    
    # Actualizar puntuación máxima si se superó
    if score > highscore:
        highscore = score
        save_highscore(highscore)
    
    # Dibujar fondo semitransparente oscuro
    canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="gray20", stipple="gray50")    
    
    # Texto principal "GAME OVER"
    canvas.create_text(WIDTH//2, HEIGHT//2 - 50,
                       text="💔 GAME OVER",
                       fill="red", font=("Arial", 40, "bold"))
    
    # Mostrar puntuación actual
    canvas.create_text(WIDTH//2, HEIGHT//2 + 10,
                       text=f"Puntos: {score}",
                       fill="white", font=("Arial", 24))
    
    # Mostrar puntuación máxima
    canvas.create_text(WIDTH//2, HEIGHT//2 + 50,
                       text=f"Máximo: {highscore}",
                       fill="yellow", font=("Arial", 20, "bold"))
    
    # Botón de reinicio
    restart_button = tk.Button(root, text="🔄 Reiniciar", command=restart_game,
                               font=("Arial", 14, "bold"), bg="#6a0dad", fg="black",
                               padx=20, pady=10)
    canvas.create_window(WIDTH//2, HEIGHT//2 + 110, window=restart_button)

# ============================================================
# LOOP PRINCIPAL DEL JUEGO
# ============================================================
def game_loop():
    """Loop principal que actualiza el juego 30 veces por segundo"""
    global score, misses, running, game_over

    # Si el juego terminó, no continuar
    if game_over:
        return

    # Obtener posición actual del jugador
    px, py = canvas.coords(player)

    # Mover jugador a la izquierda si se presiona la flecha izquierda
    if keys["left"] and px > 40:
        canvas.move(player, -8, 0)
    
    # Mover jugador a la derecha si se presiona la flecha derecha
    if keys["right"] and px < WIDTH - 40:
        canvas.move(player, 8, 0)

    # Actualizar frutas dentro de un lock para evitar conflictos
    with lock:
        to_delete = []  # Lista de frutas a eliminar
        
        for f in foods:
            # Mover fruta hacia abajo según su velocidad
            canvas.move(f["id"], 0, food_speed)
            x, y = canvas.coords(f["id"])

            # Verificar si el jugador capturó la fruta
            if abs(x - px) < 40 and abs(y - py) < 40:
                score += 1  # Sumar 1 punto
                
                # Si es cereza, restaurar una vida
                if f["life"]:
                    misses = max(0, misses - 1)
                
                to_delete.append(f)

            # Verificar si la fruta pasó sin ser capturada
            elif y > HEIGHT:
                misses += 1  # Restar una vida
                to_delete.append(f)

        # Eliminar frutas del canvas y de la lista
        for f in to_delete:
            canvas.delete(f["id"])
            foods.remove(f)

    # ========== DIBUJAR PANEL DE INFORMACIÓN ==========
    # Crear rectángulo blanco para el panel de puntuación (transparente)
    canvas.create_rectangle(0, 0, 200, 140, fill="white", outline="", stipple="gray50")

    # Título del juego
    canvas.create_text(350, 20, text="Snoopy",
                       fill="#6a0dad", font=("Comic Sans MS", 22, "bold"))

    # Mostrar puntuación actual
    canvas.create_text(70, 60, text=f"Puntos: {score}",
                       fill="black", font=("Arial", 16))
    
    # Mostrar vidas restantes
    canvas.create_text(70, 85, text=f"Vidas: {MAX_MISSES - misses}",
                       fill="black", font=("Arial", 16))
    
    # Mostrar puntuación máxima
    canvas.create_text(70, 110, text=f"Máximo: {highscore}",
                       fill="#6a0dad", font=("Arial", 14, "bold"))

    # ========== VERIFICAR FIN DEL JUEGO ==========
    if misses >= MAX_MISSES:
        game_over = True  # Activar flag de fin de juego
        show_game_over()  # Mostrar pantalla de Game Over
        return  # Salir del loop

    # Repetir este loop después de 30ms (33 fps aproximadamente)
    root.after(30, game_loop)

# Iniciar el loop principal
game_loop()

# Iniciar la ventana (loop de eventos de tkinter)
root.mainloop()
