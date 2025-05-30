import serial

import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Configure the serial port (update 'COM3' and baudrate as needed)
ser = serial.Serial('COM8', 9600, timeout=1)

x_data = []
y_data = []

fig, ax = plt.subplots()
line, = ax.plot([], [], 'r-')
ax.set_xlabel('Sample')
ax.set_ylabel('Value')
ax.set_title('Real-time Arduino Data')

def init():
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 1023)  # Adjust based on your sensor range
    line.set_data([], [])
    return line,

def update(frame):
    try:
        data = ser.readline().decode('utf-8').strip()
        if data:
            y = float(data)
            y_data.append(y)
            x_data.append(len(x_data))
            # Keep only the last 100 points
            x_data_trim = x_data[-100:]
            y_data_trim = y_data[-100:]
            line.set_data(x_data_trim, y_data_trim)
            ax.set_xlim(max(0, len(x_data)-100), len(x_data))
    except Exception:
        pass
    return line,

ani = animation.FuncAnimation(fig, update, init_func=init, blit=True, interval=50)

plt.show()
ser.close()