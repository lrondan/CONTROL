# industrial_scada.py
import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
import queue
from datetime import datetime

class IndustrialSCADA:
    def __init__(self, root):
        self.root = root
        self.root.title("Industrial SCADA System")
        self.root.geometry("1000x700")
        
        # Communication
        self.serial_conn = None
        self.data_queue = queue.Queue()
        self.running = True
        
        # Control variables
        self.pump_pwm = tk.IntVar(value=0)
        self.cooler_pwm = tk.IntVar(value=0)
        self.heater_angle = tk.IntVar(value=0)
        self.setpoint = tk.DoubleVar(value=25.0)  # Default setpoint
        self.hysteresis = tk.DoubleVar(value=2.0) # Default hysteresis
        self.auto_mode = tk.BooleanVar(value=True)
        
        # Data storage
        self.time_data = []
        self.temp1_data = []
        self.temp2_data = []
        
        # Create interface
        self.create_widgets()
        self.start_serial_thread()

    def create_widgets(self):
        # Configure grid weights
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        # Control Panel
        control_frame = ttk.LabelFrame(self.root, text="Manual Control", padding=10)
        control_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        # Pump Control
        ttk.Label(control_frame, text="Pump PWM (0-255):").grid(row=0, column=0, sticky="w")
        ttk.Scale(control_frame, from_=0, to=255, variable=self.pump_pwm,
                 command=lambda v: self.send_command(f"PUMP;{int(float(v))}")).grid(row=0, column=1)
        ttk.Label(control_frame, textvariable=self.pump_pwm).grid(row=0, column=2, padx=5)
        
        # Cooler Control
        ttk.Label(control_frame, text="Cooler PWM (0-255):").grid(row=1, column=0, sticky="w")
        ttk.Scale(control_frame, from_=0, to=255, variable=self.cooler_pwm,
                 command=lambda v: self.send_command(f"COOLER;{int(float(v))}")).grid(row=1, column=1)
        ttk.Label(control_frame, textvariable=self.cooler_pwm).grid(row=1, column=2, padx=5)
        
        # Heater Control
        ttk.Label(control_frame, text="Heater Angle (0-180°):").grid(row=2, column=0, sticky="w")
        ttk.Scale(control_frame, from_=0, to=180, variable=self.heater_angle,
                 command=lambda v: self.send_command(f"HEATER;{int(float(v))}")).grid(row=2, column=1)
        ttk.Label(control_frame, textvariable=self.heater_angle).grid(row=2, column=2, padx=5)
        
        # Auto Control Panel
        auto_frame = ttk.LabelFrame(self.root, text="Automatic Control", padding=10)
        auto_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)
        
        ttk.Label(auto_frame, text="Setpoint (°C):").grid(row=0, column=0)
        ttk.Entry(auto_frame, textvariable=self.setpoint, width=8).grid(row=0, column=1, padx=5)
        
        ttk.Label(auto_frame, text="Hysteresis (°C):").grid(row=1, column=0)
        ttk.Entry(auto_frame, textvariable=self.hysteresis, width=8).grid(row=1, column=1, padx=5)
        
        ttk.Checkbutton(auto_frame, text="Auto Mode", variable=self.auto_mode).grid(row=2, column=0, columnspan=2)
        
        # Connection Panel
        conn_frame = ttk.LabelFrame(self.root, text="Connection", padding=10)
        conn_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=5)
        
        self.port_combobox = ttk.Combobox(conn_frame, width=12)
        self.port_combobox.grid(row=0, column=0, padx=5)
        
        self.connect_btn = ttk.Button(conn_frame, text="Connect", command=self.toggle_connection)
        self.connect_btn.grid(row=0, column=1, padx=5)
        
        self.status_label = ttk.Label(conn_frame, text="Disconnected", foreground="red")
        self.status_label.grid(row=1, column=0, columnspan=2)
        
        # Temperature Display
        temp_frame = ttk.LabelFrame(self.root, text="Current Temperatures", padding=10)
        temp_frame.grid(row=1, column=2, sticky="nsew", padx=10, pady=5)
        
        ttk.Label(temp_frame, text="Sensor 1:").grid(row=0, column=0, sticky="w")
        self.temp1_label = ttk.Label(temp_frame, text="-- °C", font=('Arial', 12))
        self.temp1_label.grid(row=0, column=1, sticky="e")
        
        ttk.Label(temp_frame, text="Sensor 2:").grid(row=1, column=0, sticky="w")
        self.temp2_label = ttk.Label(temp_frame, text="-- °C", font=('Arial', 12))
        self.temp2_label.grid(row=1, column=1, sticky="e")
        
        # Graph Area
        graph_frame = ttk.Frame(self.root)
        graph_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)
        
        fig = Figure(figsize=(8, 4), dpi=100)
        self.ax = fig.add_subplot(111)
        self.temp1_line, = self.ax.plot([], [], 'r-', label='Sensor 1')
        self.temp2_line, = self.ax.plot([], [], 'b-', label='Sensor 2')
        self.ax.legend()
        self.ax.grid(True)
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Temperature (°C)")
        
        self.canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Populate serial ports
        self.update_serial_ports()

    def update_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        self.port_combobox['values'] = [port.device for port in ports]
        if ports:
            self.port_combobox.current(0)

    def toggle_connection(self):
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            self.connect_btn.config(text="Connect")
            self.status_label.config(text="Disconnected", foreground="red")
        else:
            port = self.port_combobox.get()
            try:
                self.serial_conn = serial.Serial(port, 115200, timeout=1)
                self.connect_btn.config(text="Disconnect")
                self.status_label.config(text=f"Connected to {port}", foreground="green")
            except Exception as e:
                self.status_label.config(text=f"Connection failed: {str(e)}", foreground="red")

    def send_command(self, command):
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.write(f"{command}\n".encode())

    def start_serial_thread(self):
        self.serial_thread = threading.Thread(target=self.serial_worker, daemon=True)
        self.serial_thread.start()
        
        self.update_thread = threading.Thread(target=self.update_gui, daemon=True)
        self.update_thread.start()

    def serial_worker(self):
        while self.running:
            try:
                if self.serial_conn and self.serial_conn.is_open:
                    line = self.serial_conn.readline().decode().strip()
                    if line.startswith("DATA;"):
                        parts = line.split(";")
                        if len(parts) >= 4:
                            temp1 = float(parts[1])
                            temp2 = float(parts[2])
                            timestamp = int(parts[3]) / 1000  # Convert to seconds
                            self.data_queue.put(("DATA", temp1, temp2, timestamp))
                            
                            # Automatic control if enabled
                            if self.auto_mode.get():
                                self.auto_control(temp1, temp2)
            except Exception as e:
                print(f"Serial error: {e}")
                if self.serial_conn and self.serial_conn.is_open:
                    self.serial_conn.close()
                    self.status_label.config(text="Connection lost", foreground="red")

    def auto_control(self, temp1, temp2):
        avg_temp = (temp1 + temp2) / 2
        sp = self.setpoint.get()
        hyst = self.hysteresis.get()
        
        # Cooling needed
        if avg_temp > sp + hyst:
            cooling_power = min(255, int(255 * (avg_temp - (sp + hyst)) / 10))
            self.cooler_pwm.set(cooling_power)
            self.send_command(f"COOLER;{cooling_power}")
            self.heater_angle.set(0)
            self.send_command("HEATER;0")
            
            # Pump runs at 50% when cooling
            self.pump_pwm.set(128)
            self.send_command("PUMP;128")
        
        # Heating needed
        elif avg_temp < sp - hyst:
            heating_angle = min(180, int(180 * ((sp - hyst) - avg_temp) / 10))
            self.heater_angle.set(heating_angle)
            self.send_command(f"HEATER;{heating_angle}")
            self.cooler_pwm.set(0)
            self.send_command("COOLER;0")
            
            # Pump runs at 75% when heating
            self.pump_pwm.set(192)
            self.send_command("PUMP;192")
        
        # Within deadband
        else:
            self.heater_angle.set(0)
            self.cooler_pwm.set(0)
            self.send_command("HEATER;0")
            self.send_command("COOLER;0")
            
            # Pump runs at 25% for circulation
            self.pump_pwm.set(64)
            self.send_command("PUMP;64")

    def update_gui(self):
        while self.running:
            try:
                data_type, temp1, temp2, timestamp = self.data_queue.get_nowait()
                
                # Update temperature displays
                self.temp1_label.config(text=f"{temp1:.1f} °C")
                self.temp2_label.config(text=f"{temp2:.1f} °C")
                
                # Store data for plotting
                self.time_data.append(timestamp)
                self.temp1_data.append(temp1)
                self.temp2_data.append(temp2)
                
                # Keep only the last 100 points
                if len(self.time_data) > 100:
                    self.time_data.pop(0)
                    self.temp1_data.pop(0)
                    self.temp2_data.pop(0)
                
                # Update plot
                self.temp1_line.set_data(self.time_data, self.temp1_data)
                self.temp2_line.set_data(self.time_data, self.temp2_data)
                self.ax.relim()
                self.ax.autoscale_view()
                self.canvas.draw()
                
            except queue.Empty:
                self.root.update()
                continue

    def on_closing(self):
        self.running = False
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = IndustrialSCADA(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()