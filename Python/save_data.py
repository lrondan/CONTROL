import serial
from random import randint

randname = randint(1, 1000)  # Generate a random number for the filename

port = 'COM8'  # Replace with your serial port
baudrate = 9600  # Replace with your baud rate

ser = serial.Serial(port, baudrate)  # Open the serial port

def read_data():
    try:
        while True:
            if ser.in_waiting > 0:  # Check if data is available to read
                data = ser.readline().decode('utf-8').strip()  # Read a line of data
                print(data)  # Print the data to the console
                csv_filename = f'data{randname}.csv'  # Specify the CSV file name
                with open(csv_filename, 'a') as csv_file:
                    csv_file.write(data + '\n')  # Append data to the CSV file
    except KeyboardInterrupt:  # Allow graceful exit on Ctrl+C
        print("Exiting...")  
    finally:
        ser.close()  # Close the serial port when done
        print("Serial port closed.")

if __name__ == "__main__":
    read_data()  #run the function