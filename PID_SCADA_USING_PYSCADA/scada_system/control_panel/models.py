from django.db import models

class ArduinoConfig(models.Model):
    name = models.CharField(max_length=100)
    port = models.CharField(max_length=50)
    baudrate = models.IntegerField(default=115200)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.port} @ {self.baudrate} bps)"
    
class DataLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    temp1 = models.FloatField()
    temp2 = models.FloatField()
    flow = models.FloatField()
    heater = models.FloatField()
    cooler = models.FloatField()
    setpoint = models.FloatField()
    arduino = models.ForeignKey(ArduinoConfig, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.timestamp} - Temp: {self.temp1}/{self.temp2}°C"
