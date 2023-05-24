import socket
import json
import time
import threading

# Hosted Files will be global 
hosted_files = ["image", "pepe"]

udp_port = 5001  

def send_udp_broadcast(): # Chunk Announcer
   # Create a UDP socket
   sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
   
   # Set the broadcast address and port
   broadcast_address = 'localhost'
   broadcast_endpoint = (broadcast_address, udp_port)
   data = {"chunks": hosted_files}
   json_data = json.dumps(data)

   while True:
      # Send the UDP broadcast message
      sock.sendto(json_data.encode(), broadcast_endpoint)
      time.sleep(60)

def start_tcp_server():
   host = '127.0.0.1'  # Local host
   port = 5000
   
   server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   server.bind((host, port))
   server.listen()
   
   print("TCP server started. Listening on {}:{}".format(host, port))
   
   while True:
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

   # Get Json data 
   requested_content = json_data.get("requestedcontent")
   if requested_content:
      print("Requested content:", requested_content)
      # Send requested File
      if requested_content in hosted_files:
            try:
                with open(requested_content + ".png", 'rb') as file:
                     client_socket.sendfile(file)
                     
                     # Log the downloaded file
                     log_entry = f"{time.strftime('%Y-%m-%d %H:%M:%S')}, {requested_content}, {client_socket.getpeername()[0]}\n"
                     with open("upload_log.txt", "a") as log_file:
                        log_file.write(log_entry)

            except FileNotFoundError:
               print("File not found:", requested_content)


   client_socket.close()



udp_thread = threading.Thread(target=send_udp_broadcast)
udp_thread.start()

# Start the TCP server
tcp_thread = threading.Thread(target=start_tcp_server)
tcp_thread.start()