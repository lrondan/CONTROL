from main import SCADAApp
import pandas as pd
import serial
from datetime import datetime

port = SCADAApp.get_ports
print(f"Using port: {port}")

arduino = serial.Serial(port, 9600)
data = []

try:
    while True:
        if arduino.in_waiting > 0:
            line = arduino.readline().decode().strip()
            if ':' in line:
                sensor, value = line.split(':')
                data.append({
                    'timestamp': datetime.now(),
                    'sensor': sensor,
                    'value': float(value)
                })
                # Guardar cada 10 registros
                if len(data) % 10 == 0:
                    pd.DataFrame(data).to_excel('arduino_data.xlsx', index=False)
                    
except KeyboardInterrupt:
    pd.DataFrame(data).to_excel('arduino_data.xlsx', index=False)
    arduino.close()