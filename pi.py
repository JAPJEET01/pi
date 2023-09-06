import socket
import pyaudio
import threading
import tkinter as tk
import RPi.GPIO as GPIO

# Sender configuration
SENDER_HOST = '0.0.0.0'  # Host IP
SENDER_PORT = 12345     # Port for sender
RECEIVER_IP = '192.168.53.137'  # Receiver's IP address
RECEIVER_PORT = 12346   # Port for receiver
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
MAX_PACKET_SIZE = 4096  # Maximum size of each packet

GPIO.setmode(GPIO.BCM)
gpio_pin = 17  # Change this to the actual GPIO pin number you're using
GPIO.setup(gpio_pin, GPIO.OUT)



# Initialize PyAudio
audio = pyaudio.PyAudio()
sender_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
receiver_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)

# Set up sender and receiver sockets
sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receiver_socket.bind((SENDER_HOST, RECEIVER_PORT))

ptt_active = False

def send_audio():
    while True:
        if ptt_active:
            data = sender_stream.read(CHUNK)
            for i in range(0, len(data), MAX_PACKET_SIZE):
                chunk = data[i:i+MAX_PACKET_SIZE]
                sender_socket.sendto(chunk, (RECEIVER_IP, RECEIVER_PORT))

def receive_audio():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('0.0.0.0', 12356))  # Change the port if needed

    while True:
        data, _ = server_socket.recvfrom(1024)
        if data == b'high':
            GPIO.output(gpio_pin, GPIO.LOW)
        elif data == b'low':
            GPIO.output(gpio_pin, GPIO.HIGH)
            
        data, _ = receiver_socket.recvfrom(MAX_PACKET_SIZE)
        receiver_stream.write(data)

# Start sender and receiver threads
sender_thread = threading.Thread(target=send_audio)
receiver_thread = threading.Thread(target=receive_audio)
sender_thread.start()
receiver_thread.start()

def key_pressed(event):
    global ptt_active
    if event.keysym == 'Control_L':
        ptt_active = True
        print("Talking...")

def key_released(event):
    global ptt_active
    if event.keysym == 'Control_L':
        ptt_active = False
        print("Not talking...")
        
        
        


root = tk.Tk()
root.bind('<KeyPress>', key_pressed)
root.bind('<KeyRelease>', key_released)
root.mainloop()