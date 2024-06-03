# Configure MB-BGP to support EVPN Services

BGP is used in SR-MPLS for a number of functions, namely service and link-state advertisements between nodes and inter-AS domains.  In this lab we will be using MP-BGP to advertise L2EVPN services and the service labels between our PE routers.  We will configure one P router(**sr-p001**) as the Route-Reflector, and the PE routers will connect to it to exchange service information.   



## Step 1 - Configure sr-p001 - BGP w/Route Reflection 


1. Configure BGP 

On sr-p001, we will use BGP’s route-reflector feature to avoid the iBGP requirement of maintaining a full-mesh between all peers, simplifying iBGP scale limitation and configuration. We will also statically define the router ID using its Loopback0 interface as well as leverage **neighbor-groups** for templating capabilities.

```bash
(conf)#router bgp 65001
(conf-bgp)#bgp router-id 1.1.1.1
(conf-bgp)#address-family l2vpn evpn
(conf-bgp-af)#exit
(conf-bgp)#neighbor-group RR-CLIENT
(conf-bgp-nbrgrp)#remote-as 65001
(conf-bgp-nbrgrp)#update-source Loopback0
(conf-bgp-nbrgrp)#address-family l2vpn evpn
(conf-bgp-nbrgrp-af)#route-reflector-client
(conf-bgp-nbrgrp-af)#commit
(conf-bgp-nbrgrp-af)#exit
(conf-bgp-nbrgrp)#exit
(conf-bgp)#neighbor 3.3.3.3 use neighbor-group RR-CLIENT
(conf-bgp)#neighbor 4.4.4.4 use neighbor-group RR-CLIENT
(conf-bgp)#commit
(conf-bgp)#end

```
>[!NOTE]
> We have enabled the EVPN SAFI only, so IPv4 specific commands will return null values as expected. Keep this in mind! 

Node sr-p001 is now configured as a route reflector for the l2vpn evpn address-family and will accept connections from nodes sr-pe001 and sr-pe002.

2. Validate BGP

Let's validate that our configuration is working as expected and waiting for peers to begin negoitating an adjacency. 

```bash
RP/0/RP0/CPU0:sr-p001#show bgp l2vpn evpn summ
BGP router identifier 1.1.1.1, local AS number 65001
BGP generic scan interval 60 secs
Non-stop routing is enabled
BGP table state: Active
Table ID: 0x0
BGP main routing table version 1
BGP NSR Initial initsync version 18446744073709551615 (Not Reached)
BGP NSR/ISSU Sync-Group versions 0/0
BGP scan interval 60 secs

BGP is operating in STANDALONE mode.


Process       RcvTblVer   bRIB/RIB   LabelVer  ImportVer  SendTblVer  StandbyVer
Speaker               1          1          1          0           1           0

Neighbor        Spk    AS MsgRcvd MsgSent   TblVer  InQ OutQ  Up/Down  St/PfxRcd
3.3.3.3           0 65001       0       0        0    0    0 00:00:00 Active
4.4.4.4           0 65001       0       0        0    0    0 00:00:00 Active
```

Each BGP session should be in the **Active** state. 

## Step 2 - Configure sr-pe001 and sr-pe002

Similarly to the route-reflector, we need to turn on the BGP router process, turn on the l2vpn evpn address-family, set a router-id, and configure the route-reflector as a neighbor on both PE routers.

On sr-pe001:
```bash
RP/0/RP0/CPU0:sr-pe001#conf
RP/0/RP0/CPU0:sr-pe001(config)#router bgp 65001
RP/0/RP0/CPU0:sr-pe001(config-bgp)#bgp router-id 3.3.3.3
RP/0/RP0/CPU0:sr-pe001(config-bgp)#address-family l2vpn evpn
RP/0/RP0/CPU0:sr-pe001(config-bgp-af)#exit
RP/0/RP0/CPU0:sr-pe001(config-bgp)#neighbor 1.1.1.1
RP/0/RP0/CPU0:sr-pe001(config-bgp-nbr)#remote-as 65001
RP/0/RP0/CPU0:sr-pe001(config-bgp-nbr)#update-source loopback0
RP/0/RP0/CPU0:sr-pe001(config-bgp-nbr)#address-family l2vpn evpn
RP/0/RP0/CPU0:sr-pe001(config-bgp-nbr-af)#commit
RP/0/RP0/CPU0:sr-pe001(config-bgp-nbr-af)#end
```
On sr-pe002:
```bash
RP/0/RP0/CPU0:sr-pe002#conf
RP/0/RP0/CPU0:sr-pe002(config)#router bgp 65001
RP/0/RP0/CPU0:sr-pe002(config-bgp)#bgp router-id 4.4.4.4
RP/0/RP0/CPU0:sr-pe002(config-bgp)#address-family l2vpn evpn
RP/0/RP0/CPU0:sr-pe002(config-bgp-af)#exit
RP/0/RP0/CPU0:sr-pe002(config-bgp)#neighbor 1.1.1.1
RP/0/RP0/CPU0:sr-pe002(config-bgp-nbr)#remote-as 65001
RP/0/RP0/CPU0:sr-pe002(config-bgp-nbr)#update-source loopback0
RP/0/RP0/CPU0:sr-pe002(config-bgp-nbr)#address-family l2vpn evpn
RP/0/RP0/CPU0:sr-pe002(config-bgp-nbr-af)#commit
RP/0/RP0/CPU0:sr-pe002(config-bgp-nbr-af)#end
```

## Step 3 - Validate BGP peering on nodes 

On all three nodes, sr-p001, sr-pe001, and sr-pe002, verify that the BGP sessions are established. You will not have any prefixes yet until your services are configured and utilizing BGP for control plane learning. 


On sr-p001:
```bash
RP/0/RP0/CPU0:sr-p001#sh bgp l2vpn evpn summary
<snip>

Process       RcvTblVer   bRIB/RIB   LabelVer  ImportVer  SendTblVer  StandbyVer
Speaker               1          1          1          1           1           0

Neighbor        Spk    AS MsgRcvd MsgSent   TblVer  InQ OutQ  Up/Down  St/PfxRcd
3.3.3.3           0 65001      11      11        1    0    0 00:08:18          0
4.4.4.4           0 65001       2       3        1    0    0 00:00:10          0
```

On sr-p002:
```bash
RP/0/RP0/CPU0:sr-pe001#sh bgp l2vpn evpn summ
<snip>

Process       RcvTblVer   bRIB/RIB   LabelVer  ImportVer  SendTblVer  StandbyVer
Speaker               1          1          1          1           1           0

Neighbor        Spk    AS MsgRcvd MsgSent   TblVer  InQ OutQ  Up/Down  St/PfxRcd
1.1.1.1           0 65001       6       5        1    0    0 00:03:52          0
```

On sr-pe002:
```bash
RP/0/RP0/CPU0:sr-pe002#sh bgp l2vpn evpn summ
<snip>

Process       RcvTblVer   bRIB/RIB   LabelVer  ImportVer  SendTblVer  StandbyVer
Speaker               1          1          1          1           1           0

Neighbor        Spk    AS MsgRcvd MsgSent   TblVer  InQ OutQ  Up/Down  St/PfxRcd
1.1.1.1           0 65001       6       5        1    0    0 00:03:59          0
```


## Step 4 - Replicate configuration on sr-p002

This is an optional step but will allow you to observe services ECMP through BGP. Execute steps 1 - 3 but on sr-p001 and modify the existing configuration on sr-pe001 and sr-pe002 to include a peering for sr-p002's loopback of `2.2.2.2`. 

 When this configuration is complete you should have the the following peering relationships in place: 

 Peer1      |  Peer2     
----------  | :------------ 
sr-p001     | sr-pe001 
Sr-p001     | sr-pe002 
Sr-p002     | sr-pe001 
Sr-p002     | sr-pe002   
