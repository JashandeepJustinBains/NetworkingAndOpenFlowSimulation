As an example let us use the first add-flow command in "ovs_connect_h0h1.sh". A frame arrives to switch s0 containing the following:

$ofctl add-flow s0 \  
    in_port=1,ip,nw_src=10.0.0.2,nw_dst=10.0.1.2,
    actions=mod_dl_src:0A:00:0A:01:00:02,mod_dl_dst:0A:00:0A:FE:00:02,
    output=2 

Where the following parameters correspond to:

in_port: specifies that the Frame must arrive from "in_port" value
ip: We are only on one network so this isnt super important
nw_src: the Frame has nw_src IP address of nw_src
nw_dst: the Frame has nw_dst IP address of nw_dst

Then we will effect the following

mod_dl_src: specify the source MAC address of the packet to mod_dl_src which is the MAC address that belongs to the switch

mod_dl_dst: specify the destination MAC address of the packet to mod_dl_dst which is a source port in another switch or host

output: send the packet from egress port "output"

So the first add-flow command checks if the Frame arrived to in_port=1 and has source IP 10.0.0.2 (h0) to destination IP 10.0.1.2 (h1) and allows the ports on s0 to recieve Frames from h0 that want to end up in h1. Then the switch (s0) changes the Frame's source MAC address to the current switch address (0A:00:0A:01:00:02) and change the Frame's destination MAC address to the next switches MAC address (0A:00:0A:FE:00:02). Lastly the output is which link to send the Frame to.

The next 3 add-flow commands do a similar function but in different directions and change the MAC addresses accordingly. command 2 is the same as command one but in the opposite direction so that h1 can send Frames to h0. Commands 3 and 4 are for switch s1 and are similar to commands 1 and 2.