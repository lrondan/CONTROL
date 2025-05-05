# control_panel/views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .serial_com import ArduinoCommunication
from datetime import datetime
from .models import DataLog, ArduinoConfig
import serial.tools.list_ports

arduino = ArduinoCommunication()

def dashboard(request):
    arduinos = ArduinoConfig.objects.filter(active=True)
    return render(request, 'control_panel/dashboard.html', {
        'arduinos': arduinos
    })

def system_data(request):
    data = arduino.get_data()
    if data and not data.get('error'):
        # Guardar en base de datos
        DataLog.objects.create(
            temp1=float(data['T1']),
            temp2=float(data['T2']),
            flow=float(data['F']),
            heater=float(data['H']),
            cooler=float(data['C']),
            setpoint=float(data['S'])
        )
    return JsonResponse(data if data else {'error': 'No data'})

def send_command(request, command):
    success = arduino.send_command(command)
    return JsonResponse({'status': 'success' if success else 'error'})

def historical_data(request):
    # Obtener últimos 100 registros
    data = DataLog.objects.order_by('-timestamp')[:100]
    return JsonResponse({
        'labels': [d.timestamp.isoformat() for d in data],
        'temp1': [d.temp1 for d in data],
        'temp2': [d.temp2 for d in data],
        'flow': [d.flow for d in data],
        'heater': [d.heater for d in data],
        'cooler': [d.cooler for d in data],
        'setpoint': [d.setpoint for d in data]
    })

def update_arduino_config(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        port = request.POST.get('port')
        baudrate = request.POST.get('baudrate')
        
        ArduinoConfig.objects.update_or_create(
            port=port,
            defaults={
                'name': name,
                'baudrate': baudrate,
                'active': True
            }
        )
        return redirect('dashboard')
    
def refresh_ports(request):
    ports = list(serial.tools.list_ports.comports())
    saved_arduinos = list(ArduinoConfig.objects.values('id', 'name', 'port'))
    return JsonResponse({
        'ports': [{"port": p.device, "description": p.description} for p in ports],
        'arduinos': saved_arduinos
    })