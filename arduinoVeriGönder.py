import serial
import time # Bekleme süresi için lazım

# Port ismini (COM3 gibi) kendi portunla değiştir
arduino = serial.Serial('COM6', 9600)
time.sleep(2) # Arduino'nun uyanması için 2 saniye bekle

while True:
    komut = input("Komut (1/0): ")
    if komut in ['1', '0']:
        arduino.write(komut.encode()) 
    elif komut == 'exit':
        break

arduino.close()