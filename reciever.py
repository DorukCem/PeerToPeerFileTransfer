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
                    print("Content Dictionary:", content_dictionary)

        except json.JSONDecodeError:
            print("Error parsing JSON message:", message)

 
def start_tcp_connection(ip_address):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((ip_address, 5000))
    print("Initiating TCP connection with", ip_address)

    message = input("please enter the file that you want: ")
    request = {
        "requestedcontent": message
    }

    json_request = json.dumps(request)
    client.send(json_request.encode('ascii'))


    recieve(client)

def recieve(client):
    
# Create a buffer to store received data
    buffer = b""

    while True:
        # Receive a chunk of data from the client
        data = client.recv(1024)
        if not data:
            break
        
        # Append the received data to the buffer
        buffer += data
    
    # Save the received file
    with open("received_file.png", "wb") as file:
        file.write(buffer)
        file.close()
    
    
    print("File received and saved as 'received_file'")



if __name__ == "__main__":
    # Start listening for UDP broadcast messages in a separate thread
    udp_thread = threading.Thread(target=listen_udp_broadcast, args=(5001,))
    udp_thread.start()
    
    tcp_thread = threading.Thread(target=start_tcp_connection, args=('localhost',))
    tcp_thread.start()