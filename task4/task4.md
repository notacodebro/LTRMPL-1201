# Configure IOS routers for OSPF in Server Overlay 

In this Task we will configure a second EVPN VPWS to create a Layer 2 adjacency between two IOS-XE L3 switches.  These switches are pre-configured with a loopback and routed interfaces.  We will need to start an OSPF process and ensure and adjacency forms.  Since these interfaces are in the overlay, the underlay's OSPF domain will not interact with them.

## Step 1: Configure EVPN service for IOS-XE L3 Switches

1. Create the EVPN service.

```
EVI:  1002
sr-pe001 AC-ID: 11002
sr-pe002 AC-ID: 21002
AC interface ID of both routers: Hu0/0/0/2
dot1q tag:  untagged
```

On sr-pe001:
```bash
(config)#int hu0/0/0/2
(config-if)#no shut
(config-if)#int hu0/0/0/2.1 l2transport
(config-subif)#encapsulation untagged
(config-subif)#no shut
(config-subif)#l2vpn
(config-l2vpn)#xconnect group routers
(config-l2vpn-xc)#p2p UNTAGGED
(config-l2vpn-xc-p2p)#interface hu0/0/0/2.1
(config-l2vpn-xc-p2p)#neighbor evpn evi 1002 target 21002
(config-l2vpn-xc-p2p-pw)#commit
(config-l2vpn-xc-p2p-pw)#end
```

On sr-pe002:
```bash
(config)#int hu0/0/0/2
(config-if)#no shut
(config-if)#int hu0/0/0/2.1 l2transport
(config-subif)#encapsulation untagged
(config-subif)#no shut
(config-subif)#l2vpn
(config-l2vpn)#xconnect group routers
(config-l2vpn-xc)#p2p UNTAGGED
(config-l2vpn-xc-p2p)#interface hu0/0/0/2.1
(config-l2vpn-xc-p2p)#neighbor evpn evi 1002 target 11002
(config-l2vpn-xc-p2p-pw)#commit
(config-l2vpn-xc-p2p-pw)#end
```

## Step 2: Configure IOS-XE switches
Log in to sr-rtr001 and sr-rtr002.  The password is 'cisco' without the quotes.  Review the routed interfaces in the default vrf.

sr-rtr001:
```bash
show ip int brief
```
```
Interface           IP-Address      OK?     Method  Status                  Protocol
GigabitEthernet0/0  198.18.128.60   YES     NVRAM   up                      up
GigabitEthernet0/1  unassigned      YES     NVRAM   administratively down   down 
GigabitEthernet0/2  10.10.2.1       YES     NVRAM   up                      up
GigabitEthernet0/3  unassigned      YES     NVRAM   administratively down   down 
Loopback0           33.33.33.33     YES     NVRAM   up                      up
```
The routed interfaces we want advertised in OSPF are Gi0/2 and Loopback0.

sr-rtr002:
```bash
sh ip int br
```
```
Interface           IP-Address      OK?     Method Status                   Protocol
GigabitEthernet0/0  198.18.128.61   YES     NVRAM up                        up
GigabitEthernet0/1  unassigned      YES     NVRAM administratively down     down
GigabitEthernet0/2  10.10.2.2       YES     NVRAM up                        up
GigabitEthernet0/3  unassigned      YES     NVRAM administratively down     down
Loopback0           44.44.44.44     YES     NVRAM up                        up
```
The routed inferfaces we want advertised in OSPF are Gi0/2 and Loopback0.

In IOS-XE, we can create OSPF interfaces based on the network membership.  On sr-rtr001, we want to advertise on all interfaces belonging to network 10.10.2.0/24 and 33.33.33.33/32.  On sr-rtr002, we want to advertise on all interfaces belonging to 10.10.2.0/24 and 44.44.44.44/32.

Run the following script on sr-rtr001:
```bash
(config)#router ospf 1
(config-router)#network 10.10.2.0 0.0.0.255 area 0
(config-router)#network 33.33.33.33 0.0.0.0 area 1
(config-router)#end
#wr
```

Run this script on sr-rtr002:
```bash
(config)#router ospf 1
(config-router)#network 10.10.2.0 0.0.0.255 area 0
(config-router)#network 44.44.44.44 0.0.0.0 area 2
(config-router)#end
#wr
```

## Step 3: Verify the Underlay
Check the PE Nodes' BGP process to ensure the service is being advertised.

On sr-pe001:
```bash
show bgp l2vpn evpn
```
```bash
Status codes: s suppressed, d damped, h history, * valid, > best
i - internal, r RIB-failure, S stale, N Nexthop-discard
Origin codes: i - IGP, e - EGP, ? - incomplete
   Network            Next Hop            Metric LocPrf Weight Path
Route Distinguisher: 3.3.3.3:1001 (default for vrf VPWS:1001)
Route Distinguisher Version: 6
*> [1][0000.0000.0000.0000.0000][11001]/120
                      0.0.0.0                                0 i
*>i[1][0000.0000.0000.0000.0000][21001]/120
                      4.4.4.4                       100      0 i
Route Distinguisher: 3.3.3.3:1002 (default for vrf VPWS:1002)
Route Distinguisher Version: 9
*> [1][0000.0000.0000.0000.0000][11002]/120
                      0.0.0.0                                0 i
*>i[1][0000.0000.0000.0000.0000][21002]/120
                      4.4.4.4                       100      0 i
Route Distinguisher: 4.4.4.4:1001
Route Distinguisher Version: 5
*>i[1][0000.0000.0000.0000.0000][21001]/120
                      4.4.4.4                       100      0 i
* i                   4.4.4.4                       100      0 i
Route Distinguisher: 4.4.4.4:1002
Route Distinguisher Version: 8
*>i[1][0000.0000.0000.0000.0000][21002]/120
                      4.4.4.4                       100      0 i
* i                   4.4.4.4                       100      0 i
```
Yes, the local router is advertising RD 3.3.3.3:1002 and is receiving RD 4.4.4.4:1002.

Check the MPLS forwarding table on sr-pe001:
```bash
show mpls forwarding
```
```
Thu May 2 14:28:42.211 UTC
Local  Outgoing    Prefix             Outgoing     Next Hop        Bytes       
Label  Label       or ID              Interface                    Switched    
------ ----------- ------------------ ------------ --------------- ------------
16001  Pop         SR Pfx (idx 1)     Hu0/0/0/0    10.1.11.1       0           
       16001       SR Pfx (idx 1)     Hu0/0/0/1    10.1.21.1       0            (!)
16002  Pop         SR Pfx (idx 2)     Hu0/0/0/1    10.1.21.1       0           
       16002       SR Pfx (idx 2)     Hu0/0/0/0    10.1.11.1       0            (!)
16004  16004       SR Pfx (idx 4)     Hu0/0/0/0    10.1.11.1       33952       
       16004       SR Pfx (idx 4)     Hu0/0/0/1    10.1.21.1       34160       
24000  Pop         SR Adj (idx 0)     Hu0/0/0/1    10.1.21.1       0           
24001  Pop         SR Adj (idx 0)     Hu0/0/0/1    10.1.21.1       0           
       16002       SR Adj (idx 0)     Hu0/0/0/0    10.1.11.1       0            (!)
24002  Pop         SR Adj (idx 0)     Hu0/0/0/0    10.1.11.1       0           
24003  Pop         SR Adj (idx 0)     Hu0/0/0/0    10.1.11.1       0           
       16001       SR Adj (idx 0)     Hu0/0/0/1    10.1.21.1       0            (!)
24004  Pop         PW(EVI=1001 AC-ID=21001)   \
                                      Hu0/0/0/4.1  point2point     0           
24005  Pop         PW(EVI=1002 AC-ID=21002)   \
                                      Hu0/0/0/2.1  point2point     0 
```

The new service on the remote node has a label of 24005, and its in our MPLS table.

## Step 4: Verify the Overlay
Return to the L3 switches to verify the two have become OSPF neighbors.  On sr-rtr001:
```bash
show ip ospf neighbor
```
```
Neighbor ID     Pri     State   Dead Time   Address     Interface
44.44.44.44     1       FULL/DR 00:00:38    10.10.2.2   GigabitEthernet0/2
```
And on sr-rtr002:
```bash
show ip ospf neighbor
```
```an
Neighbor ID     Pri State       Dead Time   Address     Interface
33.33.33.33     1   FULL/BDR    00:00:35    10.10.2.1   GigabitEthernet0/2
```
Verify the route tables on both switches.  on sr-rtr001:
```bash
show ip route
```
```
<snip>
10.0.0.0/8 is variably subnetted, 2 subnets, 2 masks
C       10.10.2.0/24 is directly connected, GigabitEthernet0/2
L       10.10.2.1/32 is directly connected, GigabitEthernet0/2 
33.0.0.0/32 is subnetted, 1 subnets
C       33.33.33.33 is directly connected, Loopback0
44.0.0.0/32 is subnetted, 1 subnets
O IA    44.44.44.44 [110/2] via 10.10.2.2, 00:03:14, GigabitEthernet0/2
```
on sr-rtr002:
```bash
show ip route
```
```
<snip>
      10.0.0.0/8 is variably subnetted, 2 subnets, 2 masks
C        10.10.2.0/24 is directly connected, GigabitEthernet0/2
L        10.10.2.1/32 is directly connected, GigabitEthernet0/2
      33.0.0.0/32 is subnetted, 1 subnets
C        33.33.33.33 is directly connected, Loopback0
      44.0.0.0/32 is subnetted, 1 subnets
O IA     44.44.44.44 [110/2] via 10.10.2.2, 00:03:24, GigabitEthernet0/2
```
Now ping from sr-rtr001's loopback to sr-rtr002's loopback:
```bash
ping 44.44.44.44 source lo0
```
```
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 44.44.44.44, timeout is 2 seconds:
Packet sent with a source address of 33.33.33.33
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 4/4/5 ms
```
You have now completed Task 4.  With this task, you have successfully created a Layer 2 adjacency between two L3 switches.  These two switches created an OSPF L3 adjacency across that L2 circuit and have shared their respective routing tables with one another.  If there is time, please continue to our Bonus Task, Task 5!

[Prev Task](../task3/task3.md) | [Next Task](../task5/task5.md) 
