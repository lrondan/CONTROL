import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import threading

class SCADAApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SCADA Industrial")
        self.geometry("1200x800")
        
        self.ser = None
        self.running = True
        self.data = {
            'temp1': [], 'temp2': [], 'flow': [],
            'heater': [], 'cooler': [], 'setpoint': []
        }
        
        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Configuración de gráficos
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.start_serial_thread()

    def create_widgets(self):
        control_frame = ttk.Frame(self)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Selección de puerto serial
        ttk.Label(control_frame, text="Puerto:").pack(side=tk.LEFT)
        self.port_combo = ttk.Combobox(control_frame, values=self.get_ports())
        self.port_combo.pack(side=tk.LEFT, padx=5)
        
        self.btn_connect = ttk.Button(control_frame, text="Conectar", 
                                    command=self.toggle_connection)
        self.btn_connect.pack(side=tk.LEFT, padx=5)
        
        # Parámetros de control
        pid_frame = ttk.LabelFrame(self, text="Control PID")
        pid_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(pid_frame, text="Setpoint:").grid(row=0, column=0)
        self.setpoint_entry = ttk.Entry(pid_frame)
        self.setpoint_entry.insert(0, "50.0")
        self.setpoint_entry.grid(row=0, column=1)
        ttk.Button(pid_frame, text="Enviar", 
                 command=lambda: self.send_command(f"SETP:{self.setpoint_entry.get()}")).grid(row=0, column=2)
        
        ttk.Label(pid_frame, text="Kp:").grid(row=1, column=0)
        self.kp_entry = ttk.Entry(pid_frame)
        self.kp_entry.insert(0, "2.0")
        self.kp_entry.grid(row=1, column=1)
        ttk.Button(pid_frame, text="Enviar", 
                 command=lambda: self.send_command(f"KP:{self.kp_entry.get()}")).grid(row=1, column=2)
        
        ttk.Label(pid_frame, text="Ki:").grid(row=2, column=0)
        self.ki_entry = ttk.Entry(pid_frame)
        self.ki_entry.insert(0, "0.1")
        self.ki_entry.grid(row=2, column=1)
        ttk.Button(pid_frame, text="Enviar", 
                 command=lambda: self.send_command(f"KI:{self.ki_entry.get()}")).grid(row=2, column=2)
        
        ttk.Label(pid_frame, text="Kd:").grid(row=3, column=0)
        self.kd_entry = ttk.Entry(pid_frame)
        self.kd_entry.insert(0, "0.5")
        self.kd_entry.grid(row=3, column=1)
        ttk.Button(pid_frame, text="Enviar", 
                 command=lambda: self.send_command(f"KD:{self.kd_entry.get()}")).grid(row=3, column=2)
        
        # Botón de emergencia
        ttk.Button(control_frame, text="PARO EMERGENCIA", 
                 command=lambda: self.send_command("EMSTOP"), 
                 style="Emergency.TButton").pack(side=tk.RIGHT)

    def get_ports(self):
        return [port.device for port in serial.tools.list_ports.comports()]

    def toggle_connection(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.btn_connect.config(text="Conectar")
        else:
            try:
                self.ser = serial.Serial(self.port_combo.get(), 115200, timeout=1)
                self.btn_connect.config(text="Desconectar")
            except Exception as e:
                print("Error de conexión:", str(e))

    def start_serial_thread(self):
        self.serial_thread = threading.Thread(target=self.read_serial)
        self.serial_thread.daemon = True
        self.serial_thread.start()

    def read_serial(self):
        while self.running:
            if self.ser and self.ser.is_open:
                try:
                    line = self.ser.readline().decode().strip()
                    if line.startswith("<") and line.endswith(">"):
                        self.process_data(line[1:-1])
                        self.update_plots()
                except UnicodeDecodeError:
                    pass

    def process_data(self, data):
        try:
            parts = data.split(',')
            values = {}
            for part in parts:
                key, val = part.split(':')
                values[key] = float(val)
            
            self.data['temp1'].append(values['T1'])
            self.data['temp2'].append(values['T2'])
            self.data['flow'].append(values['F'])
            self.data['heater'].append(values['H'])
            self.data['cooler'].append(values['C'])
            self.data['setpoint'].append(float(self.setpoint_entry.get()))
            
            # Mantener máximo 100 puntos
            for key in self.data:
                if len(self.data[key]) > 100:
                    self.data[key].pop(0)
        except Exception as e:
            print("Error procesando datos:", e)

    def update_plots(self):
        self.ax1.clear()
        self.ax2.clear()
        
        # Gráfico de temperaturas
        self.ax1.plot(self.data['temp1'], label='Temp1')
        self.ax1.plot(self.data['temp2'], label='Temp2')
        self.ax1.plot(self.data['setpoint'], 'k--', label='Setpoint')
        self.ax1.set_ylabel('Temperatura (°C)')
        self.ax1.legend()
        
        # Gráfico de actuadores
        self.ax2.plot(self.data['heater'], 'r', label='Calentador')
        self.ax2.plot(self.data['cooler'], 'b', label='Enfriador')
        self.ax2.plot(self.data['flow'], 'g', label='Flujo')
        self.ax2.set_ylabel('Porcentaje (%) / Flujo (L/min)')
        self.ax2.legend()
        
        self.canvas.draw()

    def send_command(self, cmd):
        if self.ser and self.ser.is_open:
            self.ser.write(f"{cmd}\n".encode())

    def on_close(self):
        self.running = False
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.destroy()

if __name__ == "__main__":
    app = SCADAApp()
    app.mainloop()