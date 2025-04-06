import time
import matplotlib.pyplot as plt
import numpy as np

class TemperatureController:
    def __init__(self, set_point=45.0, deadband=0.5):
        self.set_point = set_point
        self.deadband = deadband
        self.heater_on = False
        self.cooler_on = False
        self.current_temp = 25.0  # Initial temperature
        
    def update(self, dt, ambient_temp=29.0):
        # Simulate temperature change based on current controls
        if self.heater_on:
            # Heating effect - temperature rises
            self.current_temp += 0.15 * dt
        elif self.cooler_on:
            # Cooling effect - temperature drops
            self.current_temp -= 0.15 * dt
        else:
            # Drift toward ambient temperature
            if self.current_temp > ambient_temp:
                self.current_temp -= 0.02 * dt
            else:
                self.current_temp += 0.02 * dt
        
        # Add some random noise to simulate real-world conditions
        self.current_temp += np.random.normal(0, 0.05)
        
        # Control logic
        if self.current_temp < (self.set_point - self.deadband/2):
            self.heater_on = True
            self.cooler_on = False
        elif self.current_temp > (self.set_point + self.deadband/2):
            self.heater_on = False
            self.cooler_on = True
        else:
            # In deadband - maintain current state
            pass
        
        return self.current_temp, self.heater_on, self.cooler_on

def simulate_control(duration=300, dt=0.1):
    controller = TemperatureController(set_point=45.0, deadband=1.0)
    
    # Data logging
    times = []
    temperatures = []
    heater_states = []
    cooler_states = []
    
    for i in range(int(duration/dt)):
        t = i * dt
        temp, heater, cooler = controller.update(dt)
        
        # Record data
        times.append(t)
        temperatures.append(temp)
        heater_states.append(heater)
        cooler_states.append(cooler)
        
        #time.sleep(dt)  #real-time operation
    
    # Plot results
    plt.figure(figsize=(12, 6))
    
    # Temperature plot
    plt.subplot(3, 1, 1)
    plt.plot(times, temperatures, label='Temperature')
    plt.axhline(controller.set_point, color='r', linestyle='--', label='Set Point')
    plt.axhline(controller.set_point + controller.deadband/2, color='g', linestyle=':', label='Deadband')
    plt.axhline(controller.set_point - controller.deadband/2, color='g', linestyle=':')
    plt.ylabel('Temperature (°C)')
    plt.title('On-Off Temperature Control Simulation (Set Point: 45°C)')
    plt.legend()
    
    # Heater state plot
    plt.subplot(3, 1, 2)
    plt.plot(times, heater_states, 'r', label='Heater')
    plt.ylabel('Heater State')
    plt.ylim(-0.1, 1.1)
    plt.legend()
    
    # Cooler state plot
    plt.subplot(3, 1, 3)
    plt.plot(times, cooler_states, 'b', label='Cooler')
    plt.ylabel('Cooler State')
    plt.xlabel('Time (seconds)')
    plt.ylim(-0.1, 1.1)
    plt.legend()
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    simulate_control(duration=300)  # Simulate for 5 minutes