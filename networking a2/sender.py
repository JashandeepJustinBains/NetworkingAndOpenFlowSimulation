from socket import *
import packet
import sys
import threading


# multithread vars so we can send and receive simultaneously
lock = threading.Lock()
cv = threading.Condition(lock)
timedout = None

# global vars 
# how many packets we send at a time
N = 1
# time counter changed whenever there is an update to a log
t = 0
# number of packets we have sent and recieved in the correct order (minimum of the window size)
acked = 0
# number of packets that have been recieved that are ahead of the ack order
recd = 0
# which packet we are currently trying to transmit
seqnum = 0
# counts the number of packets we have sent in the window but havnt acked so far 
yettoack = 0
# counts the number of duplicates received of any ack
dupes = []

# constants
num_packets = 0
max_char = 500

# open log files
seqnumlog = open("seqnum.log", "a")
acklog = open("ack.log", "a")
Nlog = open("N.log", "a")

##### How to use
##### first run network_emulator.py
#####   python3 network_emulator.py 1028 127.0.0.1 8888 1029 127.0.0.1 6666 500 0.3 1
##### run receiver.py
#####   idk what goes here yet maybe (./receiver.sh 127.0.0.1 6666 1029 arrival.log)
##### run sender.py
#####   ./sender.sh 127.0.0.1 1028 8888 200 test.txt

# writes to seqnum.log whenever we send a packet
def wSeqnumLog(seq):
    global t
    seqnumlog.write(str(t)+" "+str(seq)+" "+"\n")

# writes to N.log when we change the size of the window due to a 
# packet that is received duplicate times
def wNLog(changeinN):
    global t
    Nlog.write(str(t)+" "+str(changeinN)+" "+"\n")

# writes to ack.log when we receive an ack from receiver.py
def wACKLog(num):
    # ack is type=0
    global t
    acklog.write(str(t)+" "+str(num)+" "+"\n")

# increases num by 1 and then modulos by 32
def increment(num):
    global num_packets
    assert(num + 1 % 32 <= num_packets)
    return (num + 1) % 32
def decrement(num):
    global num_packets
    return (num - 1) % 32

# receiver(skt) receives acks from receiver.py
def receiver(skt):
    # we always want to be able to receive acknowledgments
    global acked
    global seqnum
    global yettoack
    global N
    global dupes
    global last
    global timedout
    global t
    while(True):
        # receive a packet
        typ, num, length, data = packet.Packet(skt.recv(1024)).decode()
        last = num
        
        # we need to hold the lock if we receive a packet so we can
        # update all of the global variables that have to do with
        # the window, confirmed, acked, etc.
        lock.acquire()
        # if pkt type is EOT we close the connection
        if (typ == 2):
            wSeqnumLog(num)
            break
        # when we receive an ACK pkt we need to move window to accomodate
        else:
            wACKLog(num)
            # we need to consider if the ACK is new or old
            if (num == acked):
                wACKLog(num)
                # we can increase window size if the correct packet order is arriving
                if (N == 10):
                    N = 10
                else:
                    N = N + 1
                    wNLog(N)
                
                acked = acked + 1
                yettoack = decrement(yettoack)
                t = t+1

                cv.notify_all()

            # if the packet is recieved out of order we need to ack the packet UNLESS we recieve
            # the same packet 3 times in a row then we discard all packets in the window and start at acked again
            else:
                # write down that N has changed
                N = 1
                wNLog(N)

                # which packet do we need to resend
                # record all duplicate packets sent back and if we
                if (num < num_packets):
                    dupes[num] = dupes[num] + 1
                    if dupes[num] == 3:
                        # reset which packets we need to send as well as the duplicate counter
                        dupes[num] = 0
                        seqnum = num
                        acked = num
                        yettoack = 0
                cv.notify_all()
        
        # since we processed the packet we can release the lock
        lock.release()


def sender(skt, server_address, send_port, packets, timeout):
    global seqnum
    global acked
    global dupes
    global last
    global yettoack
    global timedout
    global N
    global t 
    ### # Create the UDP socket for the sender to give to the reciever
    skt = socket(AF_INET, SOCK_DGRAM)
    skt.connect((server_address, send_port))
    
    # we need to ensure that all of the packets in the N are sent before moving on
    while (True):
        # need to acquire lock to ensure we dont eat any updates made to 
        # global vars
        lock.acquire()

        # if we have acknowledged all of the packets and confirmed all packets then we should send the 
        # EOT packet
        if (acked == len(packets)):
            pkt = packet.Packet(2, seqnum, 0, "EOT")
            skt.sendto(pkt.encode(), (server_address, send_port))
            wSeqnumLog(seqnum)
            lock.release()
            return

        # need to find a way to send minwin to maxwin number of packets at a time
        # then we need to check how many acks were recieved for that window
        # then we retransmit (yettoack) to (N)
        while (yettoack < N) & (seqnum < len(packets)):
            skt.sendto(packets[seqnum].encode(), (server_address, send_port))
            wSeqnumLog(packets[seqnum].seqnum)
            yettoack = yettoack + 1
            seqnum = increment(seqnum)
            t = t + 1

        #implement time out using lock or something
        # cv.wait will return true if cv was awoken by notification and false if awoken by timedout
        timedout = cv.wait(timeout/1000)
        # if cv timesout then we need to send the problem packet again
        if timedout == False:
            # write down that N has changed
            N = 1
            wNLog(N)
            resend = (seqnum - yettoack) % 32
            yettoack = 1
            # ensures we dont send a packet out of range (i.e the last packet)
            if (resend != len(packets)):
                skt.sendto(packets[resend].encode(), (server_address, send_port))

                wSeqnumLog(resend)
                t = t + 1
            else:
                continue
        
        lock.release()


def main(sendersocket):
    # Load command line arguments
    args = sys.argv[1:]
    server_address = args[0]
    send_port = args[1]
    receive_port = args[2]
    timeout = args[3]
    file_name = args[4]

    global num_packets
    global dupes
    global t

    if send_port == receive_port:
        raise Exception("send port and receive port are the same")
        
    try:
        send_port=int(send_port)
        receive_port=int(receive_port)
        timeout=int(timeout)
    except(Exception):
        print(send_port, receive_port, timeout, " must all be numbers")
        exit()

    # try opening the file
    try:
        file = open(file_name, 'r')
    except IOError:
        print("Could not open file " , file_name)
        exit()
   
    #create list of packets
    packets = []
    while(True):
        string = file.read(max_char)
        if not string:
            break
        # packet requires packet_type (1=data packet), sequence number of this packet, length of packet and data contained in packet
        packets.append(packet.Packet(1, num_packets, len(string), string))
        num_packets = num_packets + 1
    
    # sets duplicate counter
    dupes = [0]*num_packets
    # write N at beginning cuz FAQ says to do it
    wNLog(1)


    # bind the socket we made
    sendersocket.bind(('', receive_port))
    thread = threading.Thread(target=receiver, args=(sendersocket,))
    thread.start()
    sender(sendersocket, server_address, send_port, packets, timeout)
    thread.join()

if __name__ == '__main__':
    file1 = open("seqnum.log", "w")
    file1.close()
    file2 = open("ack.log", "w")
    file2.close()
    file3 = open("N.log", "w")
    file3.close()
    sendersocket = socket(AF_INET, SOCK_DGRAM)
    main(sendersocket)
    sendersocket.close()
