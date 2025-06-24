import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
import queue
import time
from datetime import datetime
import pandas as pd
import random

class SCADAApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SCADA System - VSEN022")
        self.geometry("1200x800")
        
        # Configuración serial
        self.serial_ports = []
        self.current_port = None
        self.baudrate = 9600
        self.serial_connection = None
        self.serial_queue = queue.Queue()
        self.running = True
        
        # Datos para gráficos
        self.time_data = []
        self.temp1_data = []
        self.temp2_data = []
        self.flow_data = []
        self.heater_data = []
        self.cooler_data = []
        self.setpoint_data = []
        
        # Interfaz
        self.create_widgets()
        
        # Iniciar hilos
        self.serial_thread = threading.Thread(target=self.serial_reader)
        self.serial_thread.daemon = True
        self.serial_thread.start()
        
        self.update_ui()
    
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel de control
        control_frame = ttk.LabelFrame(main_frame, text="Control Panel")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Configuración serial
        ttk.Label(control_frame, text="COM Port:").pack(pady=2)
        self.port_combo = ttk.Combobox(control_frame, values=self.get_ports())
        self.port_combo.pack(pady=2)
        
        ttk.Label(control_frame, text="Baudrate:").pack(pady=2)
        self.baudrate_combo = ttk.Combobox(control_frame, values=[9600, 19200, 38400, 57600, 115200])
        self.baudrate_combo.set(9600)
        self.baudrate_combo.pack(pady=2)
        
        self.connect_btn = ttk.Button(control_frame, text="Connect to", command=self.toggle_connection)
        self.connect_btn.pack(pady=10)
        
        # Parámetros PID
        ttk.Label(control_frame, text="Setpoint (°C):").pack(pady=2)
        self.setpoint_entry = ttk.Entry(control_frame)
        self.setpoint_entry.insert(0, "45.0")
        self.setpoint_entry.pack(pady=2)
        
        ttk.Label(control_frame, text="Kp:").pack(pady=2)
        self.kp_entry = ttk.Entry(control_frame)
        self.kp_entry.insert(0, "4.0")
        self.kp_entry.pack(pady=2)
        
        ttk.Label(control_frame, text="Ki:").pack(pady=2)
        self.ki_entry = ttk.Entry(control_frame)
        self.ki_entry.insert(0, "0.2")
        self.ki_entry.pack(pady=2)
        
        ttk.Label(control_frame, text="Kd:").pack(pady=2)
        self.kd_entry = ttk.Entry(control_frame)
        self.kd_entry.insert(0, "1.0")
        self.kd_entry.pack(pady=2)
        
        ttk.Button(control_frame, text="Update PID", command=self.update_pid).pack(pady=10)
        ttk.Button(control_frame, text="Save Data", command=self.save_data_in_csv).pack(pady=5)
        
        # Botón de emergencia
        ttk.Button(control_frame, text="Emergency Stop", 
                 command=self.emergency_stop, style="Emergency.TButton").pack(pady=5)
        
        # Panel de estado
        status_frame = ttk.LabelFrame(main_frame, text="Status")
        status_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        self.temp1_label = ttk.Label(status_frame, text="Temp1: --.- °C")
        self.temp1_label.pack(pady=5)
        
        self.temp2_label = ttk.Label(status_frame, text="Temp2: --.- °C")
        self.temp2_label.pack(pady=5)
        
        self.flow_label = ttk.Label(status_frame, text="FlowRate: --.- L/min")
        self.flow_label.pack(pady=5)
        
        self.heater_label = ttk.Label(status_frame, text="Heater: --%")
        self.heater_label.pack(pady=5)
        
        self.cooler_label = ttk.Label(status_frame, text="Cooler: --%")
        self.cooler_label.pack(pady=5)
        
        self.setpoint_label = ttk.Label(status_frame, text="Setpoint: --.- °C")
        self.setpoint_label.pack(pady=5)
        
        # Gráficos
        graph_frame = ttk.Frame(main_frame)
        graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        fig = Figure(figsize=(8, 6), dpi=100)
        self.ax1 = fig.add_subplot(211)
        self.ax2 = fig.add_subplot(212)
        
        self.canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Configurar gráficos
        self.ax1.set_title("Temperatures")
        self.ax1.set_ylabel("°C")
        self.ax1.grid(True)
        
        self.ax2.set_title("Status of Actuators and Flow")
        self.ax2.set_ylabel("% / L/min")
        self.ax2.grid(True)
    
    def get_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
    
    def toggle_connection(self):
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            self.connect_btn.config(text="Connect to")
        else:
            try:
                port = self.port_combo.get()
                baudrate = int(self.baudrate_combo.get())
                self.serial_connection = serial.Serial(port, baudrate, timeout=1)
                self.connect_btn.config(text="Disconnect")
            except Exception as e:
                print(f"Error de conexión: {e}")
    
    def serial_reader(self):
        while self.running:
            if self.serial_connection and self.serial_connection.is_open:
                try:
                    line = self.serial_connection.readline().decode().strip()
                    if line.startswith("T1:") and "," in line:
                        self.process_data(line)
                except Exception as e:
                    print(f"Error serial: {e}")
            time.sleep(0.1)
    
    def process_data(self, data):
        try:
            parts = data.split(',')
            values = {}
            for part in parts:
                if ':' in part:
                    key, val = part.split(':', 1)
                    values[key.strip()] = val.strip()
            
            # Guardar datos
            self.time_data.append(datetime.now())
            self.temp1_data.append(float(values['T1']))
            self.temp2_data.append(float(values['T2']))
            self.flow_data.append(float(values['F']))
            self.heater_data.append(float(values['H']))
            self.cooler_data.append(float(values['C']))
            self.setpoint_data.append(float(values['S']))
            
            # Limitar datos a 50 puntos
            max_points = 50
            for data_list in [self.time_data, self.temp1_data, self.temp2_data, 
                             self.flow_data, self.heater_data, self.cooler_data,
                             self.setpoint_data]:
                if len(data_list) > max_points:
                    data_list.pop(0)
            
        except Exception as e:
            print(f"Error: {e}")

    def save_data_in_csv(self):
        random_number = random.randint(1, 1000000)
        try:
            data = {
                'Time': self.time_data,
                'Temp1': self.temp1_data,
                'Temp2': self.temp2_data,
                'FlowRate': self.flow_data,
                'Heater': self.heater_data,
                'Cooler': self.cooler_data,
                'Setpoint': self.setpoint_data
            }
            df = pd.DataFrame(data)
            df.to_csv(f'data_{random_number}.csv', index=False)
            print("Data saved to data.csv")
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def update_ui(self):
        if self.time_data:
            # Actualizar gráficos
            self.ax1.clear()
            self.ax2.clear()
            
            # Gráfico de temperaturas
            self.ax1.plot(self.time_data, self.temp1_data, label='Temp1')
            self.ax1.plot(self.time_data, self.temp2_data, label='Temp2')
            self.ax1.plot(self.time_data, self.setpoint_data, 'k--', label='Setpoint')
            self.ax1.legend()
            self.ax1.set_ylabel("°C")
            self.ax1.grid(True)
            
            # Gráfico de actuadores y flujo
            self.ax2.plot(self.time_data, self.heater_data, 'r', label='Calentador')
            self.ax2.plot(self.time_data, self.cooler_data, 'b', label='Enfriador')
            self.ax2.plot(self.time_data, self.flow_data, 'g', label='Flujo')
            self.ax2.legend()
            self.ax2.grid(True)
            
            self.canvas.draw()
            
            # Actualizar etiquetas
            self.temp1_label.config(text=f"Temp1: {self.temp1_data[-1]:.1f} °C")
            self.temp2_label.config(text=f"Temp2: {self.temp2_data[-1]:.1f} °C")
            self.flow_label.config(text=f"Flujo: {self.flow_data[-1]:.1f} L/min")
            self.heater_label.config(text=f"Calentador: {self.heater_data[-1]:.1f}%")
            self.cooler_label.config(text=f"Enfriador: {self.cooler_data[-1]:.1f}%")
            self.setpoint_label.config(text=f"Setpoint: {self.setpoint_data[-1]:.1f} °C")
        
        self.after(1000, self.update_ui)
    
    def update_pid(self):
        if self.serial_connection and self.serial_connection.is_open:
            try:
                setpoint = self.setpoint_entry.get()
                kp = self.kp_entry.get()
                ki = self.ki_entry.get()
                kd = self.kd_entry.get()
                
                commands = [
                    f"SETP:{setpoint}",
                    f"KP:{kp}",
                    f"KI:{ki}",
                    f"KD:{kd}",
                ]
                
                for cmd in commands:
                    self.serial_connection.write(f"{cmd}\n".encode())
                    time.sleep(0.1)
                
            except ValueError:
                print("Error: Valores inválidos")
    
    def emergency_stop(self):
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.write(b"EMSTOP\n")
    
    def on_close(self):
        self.running = False
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
        self.destroy()

if __name__ == "__main__":
    app = SCADAApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()