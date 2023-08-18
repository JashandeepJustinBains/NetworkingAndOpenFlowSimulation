#!/usr/bin/env bash

# Sets bridge to use OpenFlow 1.3
ovs-vsctl set bridge s1 protocols=OpenFlow13
ovs-vsctl set bridge s2 protocols=OpenFlow13
ovs-vsctl set bridge s3 protocols=OpenFlow13
ovs-vsctl set bridge r1 protocols=OpenFlow13
ovs-vsctl set bridge r2 protocols=OpenFlow13

# Print the protocols that each switch supports
for switch in s1 s2 s3 r1 r2
do
    protos=$(ovs-vsctl get bridge $switch protocols)
    echo "Switch $switch supports $protos"
done

ofctl='ovs-ofctl -O OpenFlow13'

#alice and bob
# need to connect:
#   s1
$ofctl add-flow s1 \
    in_port=1,actions=output:2
$ofctl add-flow s1 \
    in_port=2,actions=mod_dl_dst:aa:aa:aa:aa:aa:aa,output:1
#   r1
$ofctl add-flow r1 \
    in_port=1,actions=output:2
$ofctl add-flow r1 \
    in_port=2,actions=output:1
#   s2
$ofctl add-flow s2 \
    in_port=3,actions=mod_dl_dst:b0:b0:b0:b0:b0:b0,output:1
$ofctl add-flow s2 \
    in_port=1,actions=output:3

#david to carol
#need to connect:
#   s2
$ofctl add-flow s2 \
    in_port=2,actions=output:4
$ofctl add-flow s2 \
    in_port=4,actions=mod_dl_dst:d0:d0:d0:d0:d0:d0,output:2
#   r2
$ofctl add-flow r2 \
    in_port=1,actions=output:2
$ofctl add-flow r2 \
    in_port=2,actions=output:1
#   s3
$ofctl add-flow s3 \
    in_port=1,actions=output:2
$ofctl add-flow s3 \
    in_port=2,actions=mod_dl_dst:cc:cc:cc:cc:cc:cc,output:1

for switch in s1 s2 s3 r1 r2;
do
    echo "Flows installed in $switch:"
    $ofct dump-flows $switch
    echo ""
done

