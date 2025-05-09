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
We will have two Route-Reflectors in this AS.  We need to configure a Cluster-ID when we peer them with each other to guarantee proper route advertisements

```bash
(config-bgp)#neighbor-group RR-CLUSTER
config-bgp-nbrgrp)#remote-as 65001
(config-bgp-nbrgrp)#update-source lo0
(config-bgp-nbrgrp)#address-family l2vpn evpn
(config-bgp-nbrgrp-af)#cluster-id 1
(config-bgp-nbrgrp)#exit
(config-bgp)#neighbor 2.2.2.2 use neighbor-group RR-CLUSTER
(config-bgp)#commit

```
2.  Configure BGP on sr-p002

Execute the preceeding configuration changes but on sr-p002 with an update-source of Loopback0 of `2.2.2.2`. 

>[!NOTE]
> We have enabled the EVPN SAFI only, so IPv4 specific commands will return null values as expected. Keep this in mind! 

Node sr-p001 and sr-p002 are now configured as a route reflector for the l2vpn evpn address-family and will accept connections from nodes sr-pe001 and sr-pe002.

3. Validate BGP

Let's validate that our configuration for sr-p001 and sr-p002 are successfully connected and nodes sr-p001 and sr-p002 are waiting for peers sr-pe001 and sr-pe002 to begin negotiating an adjacency. 

```bash
RP/0/RP0/CPU0:sr-p001#show bgp l2vpn evpn summ
BGP router identifier 1.1.1.1, local AS number 65001
BGP generic scan interval 60 secs
Non-stop routing is enabled
BGP table state: Active
Table ID: 0x0
BGP table nexthop route policy: 
BGP main routing table version 1
BGP NSR Initial initsync version 1 (Reached)
BGP NSR/ISSU Sync-Group versions 0/0
BGP scan interval 60 secs

BGP is operating in STANDALONE mode.


Process    RcvTblVer     bRIB/RIB     LabelVer    ImportVer    SendTblVer   StandbyVer
Speaker            1             1             1             1             1             0

Neighbor        Spk    AS MsgRcvd MsgSent       TblVer  InQ OutQ  Up/Down  St/PfxRcd
2.2.2.2           0 65001       7       7            1    0    0 00:04:58          0
3.3.3.3           0 65001       0       0            0    0    0 00:00:00  Active
4.4.4.4           0 65001       0       0            0    0    0 00:00:00  Active
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
RP/0/RP0/CPU0:sr-pe001(config-bgp)#neighbor-group RR
RP/0/RP0/CPU0:sr-pe001(config-bgp-nbrgrp)#remote-as 65001
RP/0/RP0/CPU0:sr-pe001(config-bgp-nbrgrp)#update-source loopback0
RP/0/RP0/CPU0:sr-pe001(config-bgp-nbrgrp)#address-family l2vpn evpn
RP/0/RP0/CPU0:sr-pe001(config-bgp-nbrgrp-af)#exit
RP/0/RP0/CPU0:sr-pe001(config-bgp-nbrgrp)#exit
RP/0/RP0/CPU0:sr-pe001(config-bgp)#neighbor 1.1.1.1 use neighbor-group RR
RP/0/RP0/CPU0:sr-pe001(config-bgp)#neighbor 2.2.2.2 use neighbor-group RR
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
RP/0/RP0/CPU0:sr-pe002(config-bgp)#neighbor-group RR
RP/0/RP0/CPU0:sr-pe002(config-bgp-nbrgrp)#remote-as 65001
RP/0/RP0/CPU0:sr-pe002(config-bgp-nbrgrp)#update-source loopback0
RP/0/RP0/CPU0:sr-pe002(config-bgp-nbrgrp)#address-family l2vpn evpn
RP/0/RP0/CPU0:sr-pe002(config-bgp-nbrgrp-af)#exit
RP/0/RP0/CPU0:sr-pe002(config-bgp-nbrgrp)#exit
RP/0/RP0/CPU0:sr-pe002(config-bgp)#neighbor 1.1.1.1 use neighbor-group RR
RP/0/RP0/CPU0:sr-pe002(config-bgp)#neighbor 2.2.2.2 use neighbor-group RR
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

Neighbor        Spk    AS MsgRcvd MsgSent       TblVer  InQ OutQ  Up/Down  St/PfxRcd
2.2.2.2           0 65001      14      14            1    0    0 00:11:19          0
3.3.3.3           0 65001       2       3            1    0    0 00:00:20          0
4.4.4.4           0 65001       2       3            1    0    0 00:00:20          0
```

On sr-p002:
```bash
RP/0/RP0/CPU0:sr-pe001#sh bgp l2vpn evpn summ
<snip>

Process       RcvTblVer   bRIB/RIB   LabelVer  ImportVer  SendTblVer  StandbyVer
Speaker               1          1          1          1           1           0

Neighbor        Spk    AS MsgRcvd MsgSent       TblVer  InQ OutQ  Up/Down  St/PfxRcd
1.1.1.1           0 65001      14      14            1    0    0 00:11:19          0
3.3.3.3           0 65001       2       3            1    0    0 00:00:20          0
4.4.4.4           0 65001       2       3            1    0    0 00:00:22          0
```

On sr-pe001:
```bash
RP/0/RP0/CPU0:sr-pe001#sh bgp l2vpn evpn summ
<snip>

Process       RcvTblVer   bRIB/RIB   LabelVer  ImportVer  SendTblVer  StandbyVer
Speaker               1          1          1          1           1           0

Neighbor        Spk    AS MsgRcvd MsgSent       TblVer  InQ OutQ  Up/Down  St/PfxRcd
1.1.1.1           0 65001       3       2            1    0    0 00:00:20          0
2.2.2.2           0 65001       3       2            1    0    0 00:00:22          0
```
On sr-pe002:
```bash
RP/0/RP0/CPU0:sr-pe002#sh bgp l2vpn evpn summ
<snip>

Process       RcvTblVer   bRIB/RIB   LabelVer  ImportVer  SendTblVer  StandbyVer
Speaker               1          1          1          1           1           0

Neighbor        Spk    AS MsgRcvd MsgSent       TblVer  InQ OutQ  Up/Down  St/PfxRcd
1.1.1.1           0 65001       3       2            1    0    0 00:00:20          0
2.2.2.2           0 65001       3       2            1    0    0 00:00:22          0
```

 When this configuration is complete you should have the the following peering relationships in place: 

 SR-P001      |  SR-P002     
----------  | ------------ 
sr-pe001    | sr-pe001
sr-pe002    | sr-pe002
sr-p002     | sr-p001

[Prev Task](/../main/task1/task1.md)                                          [Next Task](/../main/task3/task3.md) 
