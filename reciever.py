import socket
import json
import datetime
import threading


content_dictionary = {}  # Global variable

def listen_udp_broadcast(port):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to the specified port
    bind_address = ('', port)
    sock.bind(bind_address)

    # Listen for UDP broadcast messages
    while True:
        data, address = sock.recvfrom(1024)
        message = data.decode()

        try:
            # Parse the message contents using JSON parser
            parsed_message = json.loads(message)

            # Get the UDP broadcast sender's IP address
            sender_ip = address[0]

            # Process the parsed message and sender's IP address
            # Update the content dictionary
            for file_name in parsed_message:
                if file_name in content_dictionary:
                    content_dictionary[file_name].add(sender_ip)
                else:
                    content_dictionary[file_name] = {sender_ip}

            # Print the updated content dictionary
            print("Content Dictionary:", content_dictionary)

        except json.JSONDecodeError:
            print("Error parsing JSON message:", message)

 

def download_file(file_name, client_socket):
    if file_name in content_dictionary:
        ip_addresses = content_dictionary[file_name]
        if len(ip_addresses) > 0:
            target_ip = ip_addresses[0]
            target_port = 5000  # Specify the TCP port for the download

            # Create a TCP socket
            sock = client_socket

            try:
               # Connect to the target IP address and port
               sock.connect((target_ip, target_port))

               # Prepare the JSON message
               message = json.dumps({"content_name": file_name})

               # Send the JSON message over the TCP connection
               sock.sendall(message.encode())

               # Receive response from the server (if applicable)
               response = sock.recv(1024)
               print(response.decode())

               # Log the download in the Download log file
               log_download(file_name, target_ip)

            except ConnectionRefusedError:
               print(f"Failed to connect to {target_ip}:{target_port}")

        else:
            print(f"No available IP addresses for {file_name}")
    else:
        print(f"{file_name} not found in the content dictionary")

def log_download(file_name, ip_address):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} - ChunkName: {file_name} - Downloaded from: {ip_address}\n"

    with open("DownloadLog.txt", "a") as file:
        file.write(log_entry)









if __name__ == "__main__":
    # Start listening for UDP broadcast messages in a separate thread
    udp_thread = threading.Thread(target=listen_udp_broadcast, args=(5001,))
    udp_thread.start()

    # Create a TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the ChunkUploader on port 5000
    chunkuploader_address = 'localhost'
    chunkuploader_port = 5000
    
    try:
        client_socket.connect((chunkuploader_address, chunkuploader_port))
    
    except ConnectionRefusedError:
        print(f"Failed to connect to ChunkUploader at {chunkuploader_address}:{chunkuploader_port}")
        client_socket.close()
        exit(1)

    # Prompt the user to enter the filename
    file_name = input("Enter the filename you want to download: ")

    # Call the download_file function
    download_file(file_name, client_socket)

    # Close the client socket
    client_socket.close()