import socket
import json
import time
import threading

# Global variables
content_dictionary = {}  
udp_port = 5001
ip_address = 

def listen_udp_broadcast():
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to the specified port
    bind_address = (ip_address, udp_port)
    sock.bind(bind_address)

    # Listen for UDP broadcast messages
    while True:
        data, address = sock.recvfrom(1024)
        message = data.decode()

        try:
            # Parse the message contents using JSON parser
            parsed_message = json.loads(message)
            chunks = parsed_message["chunks"]
            # Get the UDP broadcast sender's IP address
            sender_ip = address[0]

            # Process the parsed message and sender's IP address
            for file_name in chunks:
                if file_name in content_dictionary:
                    content_dictionary[file_name].add(sender_ip)
                else:
                    content_dictionary[file_name] = {sender_ip}

        except json.JSONDecodeError:
            print("Error parsing JSON message:", message)

 
def start_tcp_connection():
    while True:
        file_name = input("please enter the file that you want: ")
        if file_name not in content_dictionary:
            print("file not found in peers")
            continue
        ip_address = content_dictionary[file_name].copy()
        ip_address = next(iter(ip_address)) # get the first ip adress inside set

        # Start TCP
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((ip_address, 5000))
        print("Initiating TCP connection with", ip_address)

        request = {
            "requestedcontent": file_name
        }

        json_request = json.dumps(request)
        client.send(json_request.encode('ascii'))

        recieve(client, file_name) 

def recieve(client,file_name):
# Create a buffer to store received data
    buffer = b""

    while True:
        # Receive a chunk of data from the client
        data = client.recv(1024)
        if not data:
            break
        
        # Append the received data to the buffer
        buffer += data
    
    # Log Download
    log_entry = f"{time.strftime('%Y-%m-%d %H:%M:%S')}, {file_name}, {client.getpeername()[0]}\n"
    with open("download_log.txt", "a") as log_file:
        log_file.write(log_entry)


    # Save the received file
    with open(file_name + "_received.png", "wb") as file:
        file.write(buffer)
        file.close()
    
    print("File received and saved as 'received_file'")
    client.close()


if __name__ == "__main__":
    # Start listening for UDP broadcast messages in a separate thread
    udp_thread = threading.Thread(target=listen_udp_broadcast)
    udp_thread.start()
    
    tcp_thread = threading.Thread(target=start_tcp_connection)
    tcp_thread.start()