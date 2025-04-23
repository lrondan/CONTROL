import tkinter as tk
from tkinter import ttk, messagebox, Menu
import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime
import threading
import webbrowser
import os

class SCADAWithTopPanelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SCADA System for VSEN022_20_04_2025____V1.0")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        #self.root.iconbitmap(icono)
        self.root.resizable(True, True)
        
        # Control variables
        self.T_SP = tk.DoubleVar(value=45.0)
        self.HYSTERESIS = tk.DoubleVar(value=2.0)
        self.serial_connected = False
        self.available_ports = []
        
        # Data storage
        self.time_data = []
        self.temp1_data = []
        self.temp2_data = []
        self.flow_data = []
        self.heater_state = []
        self.cooler_state = []
        self.pump_state = []
        
        # Create interface
        self.create_widgets()
        self.create_menu()
        self.update_serial_ports()
        # Serial configuration
        self.serial_port = None
        self.baudrate = 9600
        self.ser = None
        
        # Start serial thread
        self.start_serial_thread()

    def create_menu(self):
        menubar = Menu(self.root)
        
        # File menu
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Requiremets", command=self.requirements)
        file_menu.add_command(label="Report", command=self.report)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Tools menu
        tools_menu = Menu(menubar, tearoff=0)
        tools_menu.add_command(label="About us", command=self.about)
        menubar.add_cascade(label="About", menu=tools_menu)
        
        self.root.config(menu=menubar)
    
    def create_widgets(self):
        # Configure grid weights
        self.root.grid_rowconfigure(2, weight=1)  # For graph area
        self.root.grid_columnconfigure(0, weight=1)
        
        # Top control frame (compact)
        control_frame = ttk.LabelFrame(self.root, text="Control Panel", padding=5)
        control_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        
        # Serial port selection
        ttk.Label(control_frame, text="Port:").grid(row=0, column=0, padx=2)
        self.port_combobox = ttk.Combobox(control_frame, width=12)
        self.port_combobox.grid(row=0, column=1, padx=2)
        
        # Setpoint and Hysteresis
        ttk.Label(control_frame, text="Setpoint:").grid(row=0, column=2, padx=2)
        ttk.Entry(control_frame, textvariable=self.T_SP, width=6).grid(row=0, column=3, padx=2)
        
        ttk.Label(control_frame, text="Hyst:").grid(row=0, column=4, padx=2)
        ttk.Entry(control_frame, textvariable=self.HYSTERESIS, width=6).grid(row=0, column=5, padx=2)
        
        # Connection button
        self.connect_btn = ttk.Button(control_frame, text="Connect", width=8, command=self.toggle_serial)
        self.connect_btn.grid(row=0, column=6, padx=5)
        
        # Attractive data panel frame
        data_panel = ttk.LabelFrame(self.root, text="Live Data", padding=10)
        data_panel.grid(row=1, column=0, sticky="ew", padx=5, pady=2)
        
        # Configure grid for data panel (2 rows, 3 columns)
        for i in range(3):
            data_panel.grid_columnconfigure(i, weight=1, uniform="data_cols")
        
        # Temperature displays
        temp1_frame = ttk.Frame(data_panel, padding=5, relief="ridge")
        temp1_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        ttk.Label(temp1_frame, text="Temperature 1", font=('Arial', 9, 'bold')).pack()
        self.temp1_display = ttk.Label(temp1_frame, text="-- °C", font=('Arial', 12, 'bold'))
        self.temp1_display.pack(pady=3)
        
        temp2_frame = ttk.Frame(data_panel, padding=5, relief="ridge")
        temp2_frame.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        ttk.Label(temp2_frame, text="Temperature 2", font=('Arial', 9, 'bold')).pack()
        self.temp2_display = ttk.Label(temp2_frame, text="-- °C", font=('Arial', 12, 'bold'))
        self.temp2_display.pack(pady=3)
        
        # Flow display
        flow_frame = ttk.Frame(data_panel, padding=5, relief="ridge")
        flow_frame.grid(row=0, column=2, sticky="nsew", padx=2, pady=2)
        ttk.Label(flow_frame, text="Flow Rate", font=('Arial', 9, 'bold')).pack()
        self.flow_display = ttk.Label(flow_frame, text="-- L/min", font=('Arial', 12, 'bold'))
        self.flow_display.pack(pady=3)
        
        # Actuator state displays
        heater_frame = ttk.Frame(data_panel, padding=5, relief="ridge")
        heater_frame.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)
        ttk.Label(heater_frame, text="Heater State", font=('Arial', 9, 'bold')).pack()
        self.heater_display = ttk.Label(heater_frame, text="OFF", font=('Arial', 12, 'bold'), foreground="red")
        self.heater_display.pack(pady=3)
        
        cooler_frame = ttk.Frame(data_panel, padding=5, relief="ridge")
        cooler_frame.grid(row=1, column=1, sticky="nsew", padx=2, pady=2)
        ttk.Label(cooler_frame, text="Cooler State", font=('Arial', 9, 'bold')).pack()
        self.cooler_display = ttk.Label(cooler_frame, text="OFF", font=('Arial', 12, 'bold'), foreground="red")
        self.cooler_display.pack(pady=3)
        
        pump_frame = ttk.Frame(data_panel, padding=5, relief="ridge")
        pump_frame.grid(row=1, column=2, sticky="nsew", padx=2, pady=2)
        ttk.Label(pump_frame, text="Pump State", font=('Arial', 9, 'bold')).pack()
        self.pump_display = ttk.Label(pump_frame, text="OFF", font=('Arial', 12, 'bold'), foreground="red")
        self.pump_display.pack(pady=3)
        
        # Graph area
        graph_area = ttk.Frame(self.root)
        graph_area.grid(row=2, column=0, sticky="nsew", padx=5, pady=2)
        
        # Configure graph area grid (1 row, 2 columns)
        graph_area.grid_columnconfigure(0, weight=3)  # Temperature gets more space
        graph_area.grid_columnconfigure(1, weight=2)  # Flow gets less space
        graph_area.grid_rowconfigure(0, weight=1)
        
        # Temperature graph
        temp_graph_frame = ttk.LabelFrame(graph_area, text="Temperature Trend", padding=2)
        temp_graph_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        self.create_temp_graph(temp_graph_frame)
        
        # Flow graph
        flow_graph_frame = ttk.LabelFrame(graph_area, text="Flow Trend", padding=2)
        flow_graph_frame.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        self.create_flow_graph(flow_graph_frame)
        
        # Actuator state graphs (below main graphs)
        state_graphs_frame = ttk.Frame(graph_area)
        state_graphs_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=2, pady=2)
        
        # Configure equal columns for state graphs
        state_graphs_frame.grid_columnconfigure(0, weight=1, uniform="states")
        state_graphs_frame.grid_columnconfigure(1, weight=1, uniform="states")
        state_graphs_frame.grid_columnconfigure(2, weight=1, uniform="states")
        
        # Heater state graph
        heater_graph_frame = ttk.LabelFrame(state_graphs_frame, text="Heater Activity", padding=2)
        heater_graph_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        self.create_heater_graph(heater_graph_frame)
        
        # Cooler state graph
        cooler_graph_frame = ttk.LabelFrame(state_graphs_frame, text="Cooler Activity", padding=2)
        cooler_graph_frame.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        self.create_cooler_graph(cooler_graph_frame)
        
        # Pump state graph
        pump_graph_frame = ttk.LabelFrame(state_graphs_frame, text="Pump Activity", padding=2)
        pump_graph_frame.grid(row=0, column=2, sticky="nsew", padx=2, pady=2)
        self.create_pump_graph(pump_graph_frame)
    
    def create_temp_graph(self, parent):
        fig = Figure(figsize=(6, 2.5), dpi=80)
        self.temp_ax = fig.add_subplot(111)
        self.temp_line1, = self.temp_ax.plot([], [], 'b-', linewidth=1, label='Temp1')
        self.temp_line2, = self.temp_ax.plot([], [], 'r-', linewidth=1, label='Temp2')
        self.temp_sp_line = self.temp_ax.axhline(self.T_SP.get(), color='g', linestyle='--', linewidth=1, label='Setpoint')
        self.temp_hi_line = self.temp_ax.axhline(self.T_SP.get()+self.HYSTERESIS.get(), color='orange', linestyle=':', linewidth=1, label='Limits')
        self.temp_lo_line = self.temp_ax.axhline(self.T_SP.get()-self.HYSTERESIS.get(), color='orange', linestyle=':')
        
        self.temp_ax.grid(True, linestyle=':', alpha=0.5)
        self.temp_ax.legend(loc='upper right', fontsize='small')
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.temp_canvas = canvas
    
    def create_flow_graph(self, parent):
        fig = Figure(figsize=(4, 2.5), dpi=80)
        self.flow_ax = fig.add_subplot(111)
        self.flow_line, = self.flow_ax.plot([], [], 'm-', linewidth=1, label='Flow')
        
        self.flow_ax.grid(True, linestyle=':', alpha=0.5)
        self.flow_ax.legend(loc='upper right', fontsize='small')
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.flow_canvas = canvas
    
    def create_heater_graph(self, parent):
        fig = Figure(figsize=(3, 1.5), dpi=80)
        self.heater_ax = fig.add_subplot(111)
        self.heater_line, = self.heater_ax.plot([], [], 'r-', linewidth=1.5, label='Heater')
        
        self.heater_ax.set_yticks([0, 1])
        self.heater_ax.set_yticklabels(['OFF', 'ON'])
        self.heater_ax.grid(True, linestyle=':', alpha=0.5)
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.heater_canvas = canvas
    
    def create_cooler_graph(self, parent):
        fig = Figure(figsize=(3, 1.5), dpi=80)
        self.cooler_ax = fig.add_subplot(111)
        self.cooler_line, = self.cooler_ax.plot([], [], 'b-', linewidth=1.5, label='Cooler')
        
        self.cooler_ax.set_yticks([0, 1])
        self.cooler_ax.set_yticklabels(['OFF', 'ON'])
        self.cooler_ax.grid(True, linestyle=':', alpha=0.5)
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.cooler_canvas = canvas
    
    def create_pump_graph(self, parent):
        fig = Figure(figsize=(3, 1.5), dpi=80)
        self.pump_ax = fig.add_subplot(111)
        self.pump_line, = self.pump_ax.plot([], [], 'g-', linewidth=1.5, label='Pump')
        
        self.pump_ax.set_yticks([0, 1])
        self.pump_ax.set_yticklabels(['OFF', 'ON'])
        self.pump_ax.grid(True, linestyle=':', alpha=0.5)
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.pump_canvas = canvas
    
    def update_serial_ports(self):
        self.available_ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combobox['values'] = self.available_ports
        if self.available_ports:
            self.port_combobox.current(0)
    
    def toggle_serial(self):
        if self.serial_connected:
            self.disconnect_serial()
        else:
            self.connect_serial()
    
    def connect_serial(self):
        selected_port = self.port_combobox.get()
        if not selected_port:
            messagebox.showerror("Error", "No serial port selected!")
            return
        
        try:
            self.ser = serial.Serial(selected_port, self.baudrate, timeout=1)
            self.serial_connected = True
            self.connect_btn.config(text="Disconnect")
            messagebox.showinfo("Success", f"Connected to {selected_port}")
        except Exception as e:
            messagebox.showerror("Error", f"Connection failed: {str(e)}")
    
    def disconnect_serial(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.serial_connected = False
        self.connect_btn.config(text="Connect")
        messagebox.showinfo("Info", "Serial connection closed")
    
    def start_serial_thread(self):
        self.serial_thread = threading.Thread(target=self.read_serial_data, daemon=True)
        self.serial_thread.start()
    
    def read_serial_data(self):
        while True:
            if self.serial_connected and self.ser and self.ser.in_waiting:
                try:
                    line = self.ser.readline().decode('utf-8').strip()
                    if line.startswith("Temp1:"):
                        self.process_data(line)
                except Exception as e:
                    print(f"Serial read error: {e}")
    
    def process_data(self, data):
        parts = data.split("|")
        try:
            # Extract values
            temp1 = float(parts[0].split(":")[1].strip())
            temp2 = float(parts[1].split(":")[1].strip())
            flow = float(parts[2].split(":")[1].strip().split(" ")[0])
            heater = int(parts[3].split(":")[1].strip())
            cooler = int(parts[4].split(":")[1].strip())
            pump = int(parts[5].split(":")[1].strip())
            
            # Update data
            current_time = datetime.now()
            self.time_data.append(current_time)
            self.temp1_data.append(temp1)
            self.temp2_data.append(temp2)
            self.flow_data.append(flow)
            self.heater_state.append(heater)
            self.cooler_state.append(cooler)
            self.pump_state.append(pump)
            
            # Keep only last 50 points
            if len(self.time_data) > 50:
                self.time_data.pop(0)
                self.temp1_data.pop(0)
                self.temp2_data.pop(0)
                self.flow_data.pop(0)
                self.heater_state.pop(0)
                self.cooler_state.pop(0)
                self.pump_state.pop(0)
            
            # Update GUI
            self.update_gui(temp1, temp2, flow, heater, cooler, pump)
            
        except Exception as e:
            print(f"Data processing error: {e}")
    
    def update_gui(self, temp1, temp2, flow, heater, cooler, pump):
        # Update data panel displays
        self.temp1_display.config(text=f"{temp1:.1f} °C")
        self.temp2_display.config(text=f"{temp2:.1f} °C")
        self.flow_display.config(text=f"{flow:.2f} L/min")
        
        # Update actuator states with colors
        heater_color = "green" if heater else "red"
        cooler_color = "green" if cooler else "red"
        pump_color = "green" if pump else "red"
        
        self.heater_display.config(text="ON" if heater else "OFF", foreground=heater_color)
        self.cooler_display.config(text="ON" if cooler else "OFF", foreground=cooler_color)
        self.pump_display.config(text="ON" if pump else "OFF", foreground=pump_color)
        
        # Update graphs
        self.update_graphs()
    
    def update_graphs(self):
        # Temperature graph
        self.temp_line1.set_data(range(len(self.temp1_data)), self.temp1_data)
        self.temp_line2.set_data(range(len(self.temp2_data)), self.temp2_data)
        self.temp_sp_line.set_ydata([self.T_SP.get()] * 2)
        self.temp_hi_line.set_ydata([self.T_SP.get() + self.HYSTERESIS.get()] * 2)
        self.temp_lo_line.set_ydata([self.T_SP.get() - self.HYSTERESIS.get()] * 2)
        self.temp_ax.relim()
        self.temp_ax.autoscale_view()
        
        # Flow graph
        self.flow_line.set_data(range(len(self.flow_data)), self.flow_data)
        self.flow_ax.relim()
        self.flow_ax.autoscale_view()
        
        # Actuator graphs
        self.heater_line.set_data(range(len(self.heater_state)), self.heater_state)
        self.cooler_line.set_data(range(len(self.cooler_state)), self.cooler_state)
        self.pump_line.set_data(range(len(self.pump_state)), self.pump_state)
        
        self.heater_ax.relim()
        self.cooler_ax.relim()
        self.pump_ax.relim()
        
        self.heater_ax.autoscale_view()
        self.cooler_ax.autoscale_view()
        self.pump_ax.autoscale_view()
        
        # Redraw all canvases
        self.temp_canvas.draw()
        self.flow_canvas.draw()
        self.heater_canvas.draw()
        self.cooler_canvas.draw()
        self.pump_canvas.draw()
    
    def requirements(self):
        try:
            messagebox.showinfo("Requirements", "1. Python 3.x\n2. Tkinter\n3. Matplotlib\n4. PySerial\n5. Webbrowser\n6. OS\n7. DateTime")
        except:
            messagebox.showerror("Error", "Index not found!")
    
    def report(self):
        """Genera y abre un reporte HTML local"""
        report_path = os.path.join("manuals", "reporte.html")
        
        # Genera contenido HTML dinámico con los datos actuales
        html_content = f"""
        <html>
        <body>
            <h1>SCADA report</h1>
            <p>last update: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            
            <h2>Data</h2>
            <ul>
                <li>Temp 1: {self.temp1_data[-1] if self.temp1_data else '--'} °C</li>
                <li>Temp 2: {self.temp2_data[-1] if self.temp2_data else '--'} °C</li>
                <li>Flow: {self.flow_data[-1] if self.flow_data else '--'} L/min</li>
            </ul>
            
            <h2>States</h2>
            <p>Heater: {'ON' if self.heater_state[-1] else 'OFF'}</p>
            <p>Cooler: {'ON' if self.cooler_state[-1] else 'OFF'}</p>
            <p>Pump1: {'ON' if self.pump_state[-1] else 'OFF'}</p>
        </body>
        </html>
        """
        
        # Guarda el archivo temporal
        with open(report_path, "w") as f:
            f.write(html_content)
        
        webbrowser.open(f"file://{os.path.abspath(report_path)}")
    
    def about(self):
        messagebox.showinfo("About", "Vanguard Community College\nSCADA System\nVersion 1.0\nDeveloped by Luis Alexis Rojas Rondan")

if __name__ == "__main__":
    root = tk.Tk()
    app = SCADAWithTopPanelApp(root)
    root.mainloop()