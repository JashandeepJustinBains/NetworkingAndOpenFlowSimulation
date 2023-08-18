from socket import *
import sys

def isInt(value):
    try:
        int(value)
    except (ValueError, TypeError):
        print('Codes must be integers OR incorrect rquest code')
        exit()

def main():
    # Load command line arguments
    args = sys.argv[1:]
    server_address = args[0]

    # arguments 1 and 2 should be integers
    isInt(args[1])
    isInt(args[2])
    n_port = int(args[1])
    request_code = int(args[2])
    
    # list of all the messages we need to send to server
    msgs = args[3:]

    ### # Create a TCP socket for negotiation
    negotiationTCP = socket(AF_INET, SOCK_STREAM)

    try:
        #close server if wrong port is given as an argument
        negotiationTCP.connect((server_address, n_port))
    except:
        print("Incorrect negotiation port code")
        exit()
    
    # Send request code to server and wait
    negotiationTCP.send(str(request_code).encode())
    r_port = negotiationTCP.recv(1024).decode()
    isInt(r_port)
    r_port = int(r_port)

    # Close TCP connection
    negotiationTCP.close()

    ### # Create the UDP socket using fetched r_port
    transactionUDP = socket(AF_INET, SOCK_DGRAM)
    transactionUDP.connect((server_address, r_port))
    
    #create list of messages
    msgs = args[3:]

    # create a loop that sends one of the messages and waits for the server
    #   to reverse them before we go to the next message
    for msg in msgs:

        transactionUDP.sendto(msg.encode(), (server_address, r_port))
        modifiedMsg = transactionUDP.recvfrom(2048)[0]
        print(modifiedMsg)
        
    #after finished reversing all messages send the 'EXIT keyword'
    finish = 'EXIT SERVER CODE YOU WILL NEVER GET THIS'
    transactionUDP.sendto(finish.encode(), (server_address, r_port))

    # close the UDP connection
    transactionUDP.close()    

if __name__ == '__main__':
    main()