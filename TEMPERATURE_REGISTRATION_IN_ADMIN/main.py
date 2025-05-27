import pandas as pd
import matplotlib.pyplot as plt

# Leer el archivo CSV generado por Arduino
df = pd.read_csv("datalog.csv", header=None, names=["Fecha", "Hora", "Temperatura (°C)", "Humedad (%)"])

# Mostrar las primeras filas
print("Datos registrados:")
print(df.head())

# Gráfico de Temperatura
plt.figure(figsize=(10, 5))
plt.plot(df["Temperatura (°C)"], label="Temperatura", color="red")
plt.title("Registro de Temperatura")
plt.xlabel("Muestras")
plt.ylabel("Temperatura (°C)")
plt.grid()
plt.legend()
plt.show()

# Gráfico de Humedad
plt.figure(figsize=(10, 5))
plt.plot(df["Humedad (%)"], label="Humedad", color="blue")
plt.title("Registro de Humedad")
plt.xlabel("Muestras")
plt.ylabel("Humedad (%)")
plt.grid()
plt.legend()
plt.show()

# Estadísticas básicas
print("\nEstadísticas:")
print(df.describe())