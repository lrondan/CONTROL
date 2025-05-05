import serial
from threading import Lock
from django.conf import settings
from .models import ArduinoConfig

class ArduinoCommunication:
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connections = {}
        return cls._instance
    
    def get_connection(self, arduino_id):
        arduino = ArduinoConfig.objects.get(id=arduino_id)
        if arduino.id not in self.connections:
            self.connections[arduino.id] = {
                'conn': None,
                'lock': Lock()
            }
        return self.connections[arduino.id]
    
    def connect(self, arduino_id):
        conn_data = self.get_connection(arduino_id)
        arduino = ArduinoConfig.objects.get(id=arduino_id)
        
        with conn_data['lock']:
            if not conn_data['conn'] or not conn_data['conn'].is_open:
                try:
                    conn_data['conn'] = serial.Serial(
                        port=arduino.port,
                        baudrate=arduino.baudrate,
                        timeout=1
                    )
                    return True
                except Exception as e:
                    print(f"Error connecting to {arduino}: {e}")
                    return False
            return conn_data['conn'].is_open
    
    def get_data(self, arduino_id):
        if not self.connect(arduino_id):
            return None
            
        conn_data = self.get_connection(arduino_id)
        with conn_data['lock']:
            try:
                conn_data['conn'].reset_input_buffer()
                conn_data['conn'].write(b"STATUS\n")
                response = conn_data['conn'].readline().decode().strip()
                
                data = {}
                for item in response.split(','):
                    if ':' in item:
                        key, value = item.split(':', 1)
                        data[key.strip()] = value.strip()
                return data
            except Exception as e:
                print(f"Read error: {e}")
                return None
    
    def send_command(self, arduino_id, command):
        if not self.connect(arduino_id):
            return False
            
        conn_data = self.get_connection(arduino_id)
        with conn_data['lock']:
            try:
                conn_data['conn'].write(f"{command}\n".encode())
                return True
            except Exception as e:
                print(f"Write error: {e}")
                return False