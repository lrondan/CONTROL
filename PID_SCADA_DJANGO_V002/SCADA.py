import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
import queue
import time

class SCADAInterface(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Control SCADA")
        self.geometry("1200x800")
        
        # Configuración serial
        self.ser = None
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
        
        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Iniciar hilo de comunicación serial
        self.serial_thread = threading.Thread(target=self.serial_reader)
        self.serial_thread.daemon = True
        self.serial_thread.start()
        
        # Actualizar interfaz periódicamente
        self.update_ui()

    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel de control izquierdo
        control_frame = ttk.LabelFrame(main_frame, text="Control PID")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Parámetros PID
        ttk.Label(control_frame, text="Setpoint (°C):").pack(pady=2)
        self.setpoint_entry = ttk.Entry(control_frame)
        self.setpoint_entry.pack(pady=2)
        self.setpoint_entry.insert(0, "50.0")
        
        ttk.Label(control_frame, text="Kp:").pack(pady=2)
        self.kp_entry = ttk.Entry(control_frame)
        self.kp_entry.pack(pady=2)
        self.kp_entry.insert(0, "2.0")
        
        ttk.Label(control_frame, text="Ki:").pack(pady=2)
        self.ki_entry = ttk.Entry(control_frame)
        self.ki_entry.pack(pady=2)
        self.ki_entry.insert(0, "0.1")
        
        ttk.Label(control_frame, text="Kd:").pack(pady=2)
        self.kd_entry = ttk.Entry(control_frame)
        self.kd_entry.pack(pady=2)
        self.kd_entry.insert(0, "0.5")
        
        ttk.Button(control_frame, text="Actualizar PID", 
                 command=self.update_pid).pack(pady=10)
        
        ttk.Button(control_frame, text="Paro Emergencia", 
                 command=self.emergency_stop, style="Emergency.TButton").pack(pady=5)
        
        # Panel de estado
        status_frame = ttk.LabelFrame(main_frame, text="Estado del Sistema")
        status_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        self.temp1_label = ttk.Label(status_frame, text="Temp1: --.- °C")
        self.temp1_label.pack(pady=5)
        
        self.temp2_label = ttk.Label(status_frame, text="Temp2: --.- °C")
        self.temp2_label.pack(pady=5)
        
        self.flow_label = ttk.Label(status_frame, text="Flujo: --.- L/min")
        self.flow_label.pack(pady=5)
        
        self.heater_label = ttk.Label(status_frame, text="Calentador: --%")
        self.heater_label.pack(pady=5)
        
        self.cooler_label = ttk.Label(status_frame, text="Enfriador: --%")
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
        self.ax1.set_title("Temperaturas")
        self.ax1.set_ylabel("°C")
        self.ax1.grid(True)
        
        self.ax2.set_title("Actuadores y Flujo")
        self.ax2.set_ylabel("% / L/min")
        self.ax2.grid(True)
        
        # Configuración serial
        serial_frame = ttk.Frame(self)
        serial_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(serial_frame, text="Puerto COM:").pack(side=tk.LEFT)
        self.port_combo = ttk.Combobox(serial_frame, values=self.get_ports())
        self.port_combo.pack(side=tk.LEFT, padx=5)
        
        self.connect_btn = ttk.Button(serial_frame, text="Conectar", 
                                    command=self.toggle_connection)
        self.connect_btn.pack(side=tk.LEFT, padx=5)
        
    def get_ports(self):
        return [port.device for port in serial.tools.list_ports.comports()]
    
    def toggle_connection(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.connect_btn.config(text="Conectar")
        else:
            try:
                self.ser = serial.Serial(self.port_combo.get(), 115200, timeout=1)
                self.connect_btn.config(text="Desconectar")
            except Exception as e:
                print("Error de conexión:", str(e))
    
    def serial_reader(self):
        while self.running:
            if self.ser and self.ser.is_open:
                try:
                    line = self.ser.readline().decode().strip()
                    if line.startswith("<") and line.endswith(">"):
                        self.process_data(line[1:-1])
                except Exception as e:
                    print("Error serial:", str(e))
            time.sleep(0.1)
    
    def process_data(self, data):
        try:
            parts = data.split(',')
            values = {}
            for part in parts:
                key, val = part.split(':')
                values[key] = float(val)
            
            # Actualizar datos para gráficos
            self.time_data.append(time.time())
            self.temp1_data.append(values['T1'])
            self.temp2_data.append(values['T2'])
            self.flow_data.append(values['F'])
            self.heater_data.append(values['H'])
            self.cooler_data.append(values['C'])
            self.setpoint_data.append(values['S'])
            
            # Mantener últimos 50 puntos
            max_points = 50
            for data_list in [self.time_data, self.temp1_data, self.temp2_data, 
                             self.flow_data, self.heater_data, self.cooler_data,
                             self.setpoint_data]:
                if len(data_list) > max_points:
                    data_list.pop(0)
            
            # Actualizar etiquetas
            self.after(0, self.update_labels, values)
            
        except Exception as e:
            print("Error procesando datos:", str(e))
    
    def update_labels(self, values):
        self.temp1_label.config(text=f"Temp1: {values['T1']:.1f} °C")
        self.temp2_label.config(text=f"Temp2: {values['T2']:.1f} °C")
        self.flow_label.config(text=f"Flujo: {values['F']:.1f} L/min")
        self.heater_label.config(text=f"Calentador: {values['H']:.1f}%")
        self.cooler_label.config(text=f"Enfriador: {values['C']:.1f}%")
        self.setpoint_label.config(text=f"Setpoint: {values['S']:.1f} °C")
    
    def update_ui(self):
        if len(self.time_data) > 1:
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
        
        self.after(1000, self.update_ui)
    
    def update_pid(self):
        if self.ser and self.ser.is_open:
            try:
                setpoint = float(self.setpoint_entry.get())
                kp = float(self.kp_entry.get())
                ki = float(self.ki_entry.get())
                kd = float(self.kd_entry.get())
                
                commands = [
                    f"SETP:{setpoint}",
                    f"KP:{kp}",
                    f"KI:{ki}",
                    f"KD:{kd}"
                ]
                
                for cmd in commands:
                    self.ser.write(f"{cmd}\n".encode())
                    time.sleep(0.1)
                
            except ValueError:
                print("Error: Valores inválidos")
    
    def emergency_stop(self):
        if self.ser and self.ser.is_open:
            self.ser.write(b"EMSTOP\n")
    
    def on_close(self):
        self.running = False
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.destroy()

if __name__ == "__main__":
    app = SCADAInterface()
    app.mainloop()