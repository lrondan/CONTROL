import serial
import time
import csv
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime

# Configuración del puerto
PORT = 'COM8'
BAUDRATE = 9600

# Abrir puerto serial
ser = serial.Serial(PORT, BAUDRATE, timeout=1)
time.sleep(2)  # Esperar a que el Arduino se inicialice

# Crear archivo CSV
csv_file = open('temperaturas.csv', mode='w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Time', 'Temperature1 (°C)', 'Temperature2 (°C)'])

# Inicialización de listas para graficar
tiempos = []
temps1 = []
temps2 = []

start_time = time.time()

# Crear gráfico
fig, ax = plt.subplots()
line1, = ax.plot([], [], label='Sensor 1')
line2, = ax.plot([], [], label='Sensor 2')

ax.set_title('Real-time Temperature Monitoring')
ax.set_xlabel('Time (s)')
ax.set_ylabel('Temperature (°C)')
ax.legend()
ax.grid(True)

def update(frame):
    try:
        data = ser.readline().decode().strip()
        if ';' in data:
            temp1_str, temp2_str = data.split(';')
            temp1 = float(temp1_str)
            temp2 = float(temp2_str)
            tiempo_actual = round(time.time() - start_time, 1)
            tiempos.append(tiempo_actual)
            temps1.append(temp1)
            temps2.append(temp2)

            # Guardar en CSV
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            csv_writer.writerow([timestamp, temp1, temp2])
            csv_file.flush()

            # Actualizar gráfico
            line1.set_data(tiempos, temps1)
            line2.set_data(tiempos, temps2)
            ax.relim()
            ax.autoscale_view()
    except Exception as e:
        print(f"Error: {e}")

    return line1, line2

ani = FuncAnimation(fig, update, interval=1000)

try:
    plt.show()
except KeyboardInterrupt:
    print("Program stopped by user.")
finally:
    ser.close()
    csv_file.close()
