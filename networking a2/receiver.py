import packet
import socket, sys


def increment(num):
    return (num + 1) % 32

# save values needed to talk to host emulator
server_address = sys.argv[1] # network host address
send_port = int(sys.argv[2]) # dest port on host
receive_port = int(sys.argv[3]) # recv port for this app
file_name = sys.argv[4] # filename to be used to record recvd data

# try opening the file
try:
    file = open(file_name, 'a')
except IOError:
    print("caint open file")
    exit()

arrival = open("arrival.log", 'a')

t = 0

# some vars needed for execution
expected = 0 # next packet # expected
skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # socket!
skt.bind(('', receive_port)) # set socket to recv on receive_port
buffer = {}
# receive pkts
while(True):
    typ, num, length, data = packet.Packet(skt.recv(2048)).decode()
    arrival.write(str(t) + " "+ str(num) + "\n")
    t = t+1
    if num == expected: # got the next packet
        if (typ == 2): # EOT packet
            # send EOT and exit
            EOTpkt = packet.Packet(2, num, 0, "EOT")
            skt.sendto(EOTpkt.encode(), (server_address,send_port))
            break
        else: # data packet
            # send ACK, record seqnum, increment expected
            # write down that data in the correct order
            file.write(data)
            # send back the highest ACK possible
            ACKpkt = packet.Packet(0, expected, 0, "ACK")
            skt.sendto(ACKpkt.encode(), (server_address, send_port))
            expected = increment(expected)

            # check buffer ?
            while expected in buffer:
                file.write(buffer[expected])
                buffer.pop(expected)
                # send back the highest ACK possible
                ACKpkt = packet.Packet(0, expected, 0, "ACK")
                skt.sendto(ACKpkt.encode(), (server_address, send_port))
                expected = increment(expected)



    else: # did not get the next expected packet so add packets to a buffer
        pkt = packet.Packet(0, expected, 0, "CONFIRM")
        skt.sendto(pkt.encode(), (server_address, send_port))
        # remove all old packets in the buffer that are 10 below expected
        for i in buffer:
            if i < expected-10:
                buffer.pop(i)

        # packet is greater than expected but less than or equal to 10 ahead
        if num > expected and (num % 32) <= ((expected - 10) % 32):
            buffer[num] = data
        
        

#file.close()
#arrival.close()
skt.close()
