from socket import *
import sys

try:
    request_code = int(sys.argv[1])
except (ValueError, TypeError):
    print('The request code must be an integer.')
    exit()

# Create TCP socket
serverSocketTCP = socket(AF_INET, SOCK_STREAM)

# find machines ipv4 address and an open port
host = gethostname()   
ip = gethostbyname(host) 
serverSocketTCP.bind((ip, 0))

serverSocketTCP.listen(1)
server_address, n_port = serverSocketTCP.getsockname()

print('SERVER_PORT=%d' %n_port)
print('SERVER_ADDRESS=%s' %server_address)

while True:
    connectionSocket, TCPaddress = serverSocketTCP.accept()
    clientRequest_code = int(connectionSocket.recv(1024).decode())
    
    if clientRequest_code != request_code:
        print("Incorrect request code given")
        break
    else:
        # Server creates a UDP socket for the transaction stage
        serverSocketUDP = socket(AF_INET, SOCK_DGRAM)
        serverSocketUDP.bind(('', 0))

        # Send r_port to client
        r_port = serverSocketUDP.getsockname()[1]
        
        connectionSocket.send(str(r_port).encode())
        
        # keep UDP connection open as long as we are receiving messages
        while True: 
            #recieves, reverses and sends the reversed message to the client
            message, UDPaddress = serverSocketUDP.recvfrom(2048)
            modifiedMessage = message.decode()[::-1]
    
            serverSocketUDP.sendto(modifiedMessage.encode(), UDPaddress)
            # when the secret code is sent then we close the UDP connection
            if (message == 'EXIT SERVER CODE YOU WILL NEVER GET THIS'):
                serverSocketUDP.close()
                break
    
serverSocketTCP.close()
