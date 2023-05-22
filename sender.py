import socket
import json
import time

def send_udp_broadcast(message, port):
   # Create a UDP socket
   sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
   
   # Set the broadcast address and port
   broadcast_address = 'localhost'
   broadcast_endpoint = (broadcast_address, port)
   
   # Send the UDP broadcast message
   sock.sendto(message.encode(), broadcast_endpoint)
   
   # Close the socket
   sock.close()

while True:
   # Create the JSON array with the hosted file
   file_name = "image.png"
   hosted_files = [file_name]
   json_data = json.dumps(hosted_files)

   # Send UDP broadcast message with the JSON data
   message = json_data
   port = 5001  # Replace with the desired port number
   send_udp_broadcast(message, port)

   # Create a TCP socket
   client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

   try:
      # Connect to the ChunkUploader on port 5000
      chunkuploader_address = 'localhost'
      chunkuploader_port = 5000
      client_socket.connect((chunkuploader_address, chunkuploader_port))

      # Prepare the JSON message
      json_message = json.dumps({"content_name": file_name})

      # Send the JSON message over the TCP connection
      client_socket.sendall(json_message.encode())

      # Receive the file data from ChunkUploader
      received_data = b""
      while True:
         data = client_socket.recv(1024)
         if not data:
               break
         received_data += data

      # Save the received file
      with open(file_name, 'wb') as file:
         file.write(received_data)

      print(f"File '{file_name}' received successfully.")

   except ConnectionRefusedError:
      print(f"Failed to connect to ChunkUploader at {chunkuploader_address}:{chunkuploader_port}")

   # Close the client socket
   client_socket.close()

   # Wait for 1 minute
   time.sleep(60)