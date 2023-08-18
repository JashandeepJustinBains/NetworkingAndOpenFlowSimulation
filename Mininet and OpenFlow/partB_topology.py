#!/usr/bin/python

from mininet.cli import CLI
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.log import setLogLevel

class CSLRTopo(Topo):

    def __init__(self):
        "Create Topology"

        # Initialize topology
        Topo.__init__(self)

        # Add hosts
        alice = self.addHost('alice')
        bob = self.addHost('bob')
        carol = self.addHost('carol')
        david = self.addHost('david')

        # Add layer-2 switches
        s1 = self.addSwitch('s1', listenPort=10000)
        s2 = self.addSwitch('s2', listenPort=10001)
        s3 = self.addSwitch('s3', listenPort=10002)
        # Add layer-3 switches
        r1 = self.addSwitch('r1', listenPort=10003)
        r2 = self.addSwitch('r2', listenPort=10004)

        # Add links between hosts and switches
        self.addLink(alice, s1)
        self.addLink(bob, s2)
        self.addLink(carol, s3)
        self.addLink(david, s2)

        # Add links between switches, with bandwidth 100Mbps
        self.addLink(s1, r1, bw=100)
        self.addLink(r1, s2, bw=100)
        self.addLink(s2, r2, bw=100)
        self.addLink(r2, s3, bw=100) 


def run():
    "Create and configure network"
    topo = CSLRTopo()
    net = Mininet(topo=topo, link=TCLink, controller=None)
    
    # Set interface IP and MAC addresses for hosts
    alice = net.get('alice')
    alice.intf('alice-eth0').setIP('10.1.1.17', 24)
    alice.intf('alice-eth0').setMAC('aa:aa:aa:aa:aa:aa')

    bob = net.get('bob')
    bob.intf('bob-eth0').setIP('10.4.4.48', 24)
    bob.intf('bob-eth0').setMAC('b0:b0:b0:b0:b0:b0')

    david = net.get('david')
    david.intf('david-eth0').setIP('10.4.4.96', 24)
    david.intf('david-eth0').setMAC('d0:d0:d0:d0:d0:d0')

    carol = net.get('carol')
    carol.intf('carol-eth0').setIP('10.6.6.69', 24)
    carol.intf('carol-eth0').setMAC('cc:cc:cc:cc:cc:cc')

    # Set interface MAC address for switches
    s1 = net.get('s1')
    s1.intf('s1-eth1').setMAC('0A:00:00:01:00:01')
    s1.intf('s1-eth2').setMAC('0A:00:0A:01:00:02')

    s2 = net.get('s2')
    s2.intf('s2-eth1').setMAC('0A:00:01:01:00:01')
    s2.intf('s2-eth2').setMAC('0A:00:0A:FE:00:02')
    s2.intf('s2-eth3').setMAC('0A:00:0B:FE:00:03')
    s2.intf('s2-eth4').setMAC('0A:00:0C:FE:00:04')

    s3 = net.get('s3')
    s3.intf('s3-eth1').setMAC('0A:00:03:01:00:01')
    s3.intf('s3-eth2').setMAC('0A:00:0D:FE:00:02')

    r1 = net.get('r1')
    r1.intf('r1-eth1').setMAC('0A:00:04:01:00:01')
    r1.intf('r1-eth2').setMAC('0A:00:0E:FE:00:02')

    r2 = net.get('r2')
    r2.intf('r2-eth1').setMAC('0A:00:05:01:00:01')
    r2.intf('r2-eth2').setMAC('0A:00:0F:FE:00:02')

    net.start()

    # Add routing table entries for hosts
    alice.cmd('route add default gw 10.1.1.14 dev alice-eth0')
    bob.cmd('route add default gw 10.4.4.14 dev bob-eth0')
    carol.cmd('route add default gw 10.6.6.46 dev carol-eth0')
    david.cmd('route add default gw 10.4.4.28 dev david-eth0')

    # Add arp cache entries for hosts
    alice.cmd('arp -s 10.1.1.14 0A:00:00:01:00:01 -i alice-eth0')
    bob.cmd('arp -s 10.4.4.14 0A:00:02:01:00:01 -i bob-eth0')
    carol.cmd('arp -s 10.6.6.46 0A:00:03:01:00:01 -i carol-eth0')
    david.cmd('arp -s 10.4.4.28 0A:00:0B:FE:00:02 -i david-eth0')

    # Open Mininet Command Line Interface
    CLI(net)

    # Teardown and cleanup
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()















