# 🎮 Snoopy Sweet Snacks con Python y Tkinter
Este proyecto es un juego arcade en 2D desarrollado con Python, utilizando la librería Tkinter para la interfaz gráfica y Pillow (PIL) para la gestión de imágenes.
El jugador controla a Snoopy, quien debe atrapar frutas que caen del cielo para sumar puntos y evitar perder todas sus vidas.

El juego aumenta progresivamente su dificultad, ofreciendo una experiencia dinámica y entretenida.

### Características
+ **Jugabilidad sencilla e intuitiva:** Controla a Snoopy con las flechas del teclado (⬅️ ➡️).
+ **Sistema de puntuación y récord:** Guarda automáticamente la puntuación máxima en un archivo local.
+ **Aumento de dificultad dinámico:** La velocidad de caída y la frecuencia de frutas incrementan conforme suben los puntos.
+ **Diferentes tipos de frutas:**
+ **🍓 Fresa: Suma puntos.**
+ **🍒 Cereza: Recupera vidas.**
+ **Pantalla de Game Over interactiva:** Muestra el puntaje final, récord y permite reiniciar el juego.
+ **Uso de hilos (threads):** Para la generación de frutas y el control de dificultad sin afectar el rendimiento.

### Tecnologías utilizadas💻
+ **Python 3: Lenguaje principal del proyecto.** 
+ **Tkinter: Creación de la interfaz gráfica y manejo de eventos.** 
+ **Pillow (PIL): Carga y redimensionamiento de imágenes.** 
+ **Threading: Ejecución paralela para la lógica del juego.** 
+ **OS & Time: Manejo de archivos y control de tiempos.**

### 🎯 Cómo jugar

Ejecuta el archivo principal del juego.

Usa las teclas:

⬅️ Flecha izquierda para moverte a la izquierda.

➡️ Flecha derecha para moverte a la derecha.

Atrapa las frutas para sumar puntos.

Evita que demasiadas frutas caigan sin atraparlas.

¡Supera tu récord y desafía la dificultad creciente!
