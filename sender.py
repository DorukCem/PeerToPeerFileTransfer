import socket
import json
import time
import threading

# Hosted Files will be global 
file_name = "image.png"
hosted_files = [file_name]


def send_udp_broadcast(message, port):
   # Create a UDP socket
   sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
   
   # Set the broadcast address and port
   broadcast_address = 'localhost'
   broadcast_endpoint = (broadcast_address, port)
   
   while True:
      # Send the UDP broadcast message
      sock.sendto(message.encode(), broadcast_endpoint)
      

def start_tcp_server():
   host = '127.0.0.1'  # Local host
   port = 5000
   
   server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   server.bind((host, port))
   server.listen()
   
   print("TCP server started. Listening on {}:{}".format(host, port))
   
   while True:
      # Accept a client connection
      client_socket, client_address = server.accept()
      
      # Handle the client connection in a separate thread
      client_thread = threading.Thread(target=handle_tcp_connection, args=(client_socket,))
      client_thread.start()


def handle_tcp_connection(client_socket):
   # Receive data from the client
   data = client_socket.recv(1024).decode()

   try:
      json_data = json.loads(data)
   except json.JSONDecodeError as e:
      print("Error parsing JSON data:", str(e))
      return

   requested_content = json_data.get("requestedcontent")
   if requested_content:
      print("Requested content:", requested_content)

      # Send requested File
      if requested_content in hosted_files:
            try:
                with open(requested_content, 'rb') as file:
                     # Send the file contents back to the client
                     client_socket.sendfile(file)

            except FileNotFoundError:
               print("File not found:", requested_content)

  
   client_socket.close()


# Create the JSON array with the hosted file
json_data = json.dumps(hosted_files)

# Send UDP broadcast message with the JSON data
message = json_data
port = 5001  

udp_thread = threading.Thread(target=send_udp_broadcast, args=(message, port))
udp_thread.start()

# Start the TCP server
tcp_thread = threading.Thread(target=start_tcp_server)
tcp_thread.start()