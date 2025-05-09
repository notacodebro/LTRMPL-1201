# Configure OSPF for the Underlay 

 The routers in the network have IP connectivity established between each other, but no routing protocols.  Since we will be using Segment Routing, we need to use a routing protocol that has been **extended** to support SR. OSPF and IS-IS have these extensions. In this task you will configure OSPF between all transport network routers, add Segment Routing and validate all configurations through various **show** commands.

```
The transport network consists of four routers:

sr-p001
sr-p002
sr-pe001
sr-pe002
```

> [!IMPORTANT] 
> Changes made in IOS-XR  do not take effect until they have been committed.  If the changes configured are not possible to be committed due to an error, none of the changes will be committed until the error has been fixed.  To commit a configuration, simply type ‘commit’.  To view the reason for an erroneous commit, type ‘commit show’. 


## Step 1 - Configure the OSPF Process

IOS-XR configures its services and protocols at the process level.  For example, all OSPF configurations occur within the ‘router ospf’ process.   Bridge domains and virtual cross connects are configured under ‘l2vpn’.  This is important as we move forward as other operating systems that you may be familiar with may be different and allow you to configure these items under their respective interfaces.

1. Configure OSPF process '1'

``` bash 
(conf)#router ospf 1
```


2. Configure Fast Re-Rroute and TI-LFA 

``` bash 
(config-ospf)#fast-reroute per-prefix
(config-ospf)#fast-reroute per-prefix ti-lfa enable


(config-ospf)#network point-to-point

(config-ospf)#segment-routing mpls
(config-ospf)#segment-routing forwarding mpls
```

> [!IMPORTANT] 
> You have just configured segment routing! That's it, it's that simple to enable segment routing extension in the routing protocol.    

<details><summary><font size=4> Expand for FRR and TI-LFA Details  </summary><pre><code></font>
Under the global configuration for OSPF we configure context, enable the fast-reroute (FRR) and topology-independent loop free alternate (TI-LFA).  By enabling it at the global OSPF context, it turns the feature on for all areas and interfaces that are using the OSPF protocol. You may also turn these on or off at the area or interface levels. <br>

For **FRR**, we have the option of using per-link or per-prefix FRR.  Per-link will create a single backup route for all routes on a specific egress link.  Per-prefix will create a backup route per route, regardless of egress link.  Per-prefix is more granular and flexible than per-link and is the recommended setting.<br>

**TI-LFA** builds a backup, loop-free labeled path to a destination prefix via an optimal routed path. This backup path is used by a transit node until the IGP finishes converging.<br>

Since our links are all point to point links, we can take advantage of OSPF’s point to point network type at the global OSPF process context as well.<br>

The last two items we need to configure in the global OSPF context before we begin configuring our Area 0 is the Segment Routing control and dataplanes.<br>
</pre></code></details>  


## Step 2 - Add Loopbacks, Configure Area backbone area

In this step you will add a loopback to each router.  The loopback is critical for both underlay and overlay control and dataplane operations. 

1. Configure loopbacks

Use the following addresses for each P and PE router, respectively:
``` bash 
Sr-p001: 1.1.1.1/32
Sr-p002: 2.2.2.2/32
Sr-pe001: 3.3.3.3/32
Sr-pe002: 4.4.4.4/32  

(config-ospf)#
(config-ospf)#int loopback0
(config-if)#ip address x.x.x.x/32 
!see list above for ip address for each router
Return to ospf configuration mode and commit changes made thus far.

(config-if)#router ospf 1
(config-ospf)# commit

```

Review the ip addresses of each P and PE router.

<details><summary><font size=4> Expand for Loopback Validation  </summary><pre><code></font>
RP/0/RP0/CPU0:sr-p001#show ip int br
Wed May  7 15:33:42.470 UTC

Interface                      IP-Address      Status          Protocol Vrf-Name
Loopback0                      1.1.1.1         Up              Up       default
HundredGigE0/0/0/0             10.1.11.1       Up              Up       default
HundredGigE0/0/0/1             10.1.21.1       Up              Up       default
HundredGigE0/0/0/2             unassigned      Shutdown        Down     default
HundredGigE0/0/0/3             10.1.33.1       Up              Up       default
HundredGigE0/0/0/4             unassigned      Shutdown        Down     default
HundredGigE0/0/0/5             unassigned      Shutdown        Down     default

</pre></code></details> <br>

2. Configure OSPF on each interface

The interfaces with ip addresses in the default vrf will need to be added to Area 0.  Proceed by adding the interfaces on each router to OSPF Area 0 and commit your changes.  Do this for all P and PE routers.   

Here is the configuration for sr-p001:
```bash
(config-ospf)#area 0
(config-ospf-ar)#int hu0/0/0/0
(config-ospf-ar-if)#exit
(config-ospf-ar)#int hu0/0/0/1
(config-ospf-ar-if)#exit
(config-ospf-ar)#int hu0/0/0/3
(config-ospf-ar-if)#exit
(config-ospf-ar)#int lo0
(config-ospf-ar)#commit
```

3. Add prefix-SID to each router's loopback 

Here are the prefix-sid absolute values for each node.  Configure these values, commit your changes, and exit configuration mode:

Device      |  Label      
----------  | :------------ 
Sr-p001     | 16001   
Sr-p002     | 16002   
Sr-pe001    | 16003   
Sr-pe002    | 16004   


> [!NOTE] 
> Ensure that you are under the OSPF process, in area 0 and configuring the loopback interfaces for the prefix-SID. 

```bash
(config-ospf-ar-if)#prefix-sid absolute xxxxx
(config-ospf-ar-if)#commit
(config-ospf-ar-if)#end
```
<details><summary><font size=4> Expand for prefix-sid details </summary><pre><code></font>
  This is like an identification label for the node.  In practice, you may use either an index or absolute value for the prefix-sid.  An index adds the value of the configured index to the starting value of the Global Segment range.  By default, the range starts at 16000 and goes to 23999, whereas an absolute value is the actual value of the label you wish to configure.   
   For example, an index of 101 will configure 16101 as the prefix-sid.  And absolute index of 17001 will configure 17001 as the prefix-sid.
</pre></code></details> <br>


## Step 3 - Validate OSPF

Check OSPF adjacencies on each node.  Nodes sr-p001 and sr-p002 should have **three** adjacencies and sr-pe001 and sr-pe002 should have **two**, each.

```bash
RP/0/RP0/CPU0:sr-p001#sh ospf nei    

* Indicates MADJ interface
# Indicates Neighbor awaiting BFD session up

Neighbors for OSPF 1

Neighbor ID     Pri   State           Dead Time   Address         Interface
3.3.3.3         1     FULL/  -        00:00:33    10.1.11.2       HundredGigE0/0/0/0
    Neighbor is up for 00:03:02
10.1.22.2       1     FULL/  -        00:00:39    10.1.12.2       HundredGigE0/0/0/1
    Neighbor is up for 00:02:52
2.2.2.2         1     FULL/  -        00:00:31    10.1.1.2        HundredGigEt0/0/0/3
    Neighbor is up for 00:02:54
```


<details><summary><font size=4> Expand for more router results</summary><pre><code></font>

```bash
RP/0/RP0/CPU0:sr-p002#show ospf nei

* Indicates MADJ interface
# Indicates Neighbor awaiting BFD session up

Neighbors for OSPF 1

Neighbor ID     Pri   State           Dead Time   Address         Interface
10.1.22.2       1     FULL/  -        00:00:39    10.1.22.2       HundredGigE0/0/0/0
    Neighbor is up for 00:03:25
3.3.3.3         1     FULL/  -        00:00:36    10.1.21.2       HundredGigE0/0/0/1
    Neighbor is up for 00:03:31
1.1.1.1         1     FULL/  -        00:00:31    10.1.1.1        HundredGigE0/0/0/3
    Neighbor is up for 00:03:28
```

```bash
RP/0/RP0/CPU0:sr-pe001#sh ospf nei

* Indicates MADJ interface
# Indicates Neighbor awaiting BFD session up

Neighbors for OSPF 1

Neighbor ID     Pri   State           Dead Time   Address         Interface
1.1.1.1         1     FULL/  -        00:00:38    10.1.11.1       HundredGigE0/0/0/0
    Neighbor is up for 00:00:22
2.2.2.2         1     FULL/  -        00:00:38    10.1.21.1       HundredGigE0/0/0/1
    Neighbor is up for 00:00:17
```
```bash
RP/0/RP0/CPU0:sr-pe002#show ospf nei

* Indicates MADJ interface
# Indicates Neighbor awaiting BFD session up

Neighbors for OSPF 1

Neighbor ID     Pri   State           Dead Time   Address         Interface
2.2.2.2         1     FULL/  -        00:00:37    10.1.22.1       HundredGigE0/0/0/0
    Neighbor is up for 00:03:50
1.1.1.1         1     FULL/  -        00:00:35    10.1.12.1       HundredGigE0/0/0/1
    Neighbor is up for 00:03:51

Total neighbor count: 2
```
</pre></code></details> <br>


Verify route tables on each node.  Look specifically that on each node you see all the loopback0 addresses of the other three nodes in the route table.   

Here is the partial output of node sr-p001:

```bash
RP/0/RP0/CPU0:sr-p001#sh ip route

Codes: C - connected, S - static, R - RIP, B - BGP, (>) - Diversion path
       D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area
       N1 - OSPF NSSA external type 1, N2 - OSPF NSSA external type 2
       E1 - OSPF external type 1, E2 - OSPF external type 2, E - EGP
       i - ISIS, L1 - IS-IS level-1, L2 - IS-IS level-2
       ia - IS-IS inter area, su - IS-IS summary null, * - candidate default
       U - per-user static route, o - ODR, L - local, G  - DAGR, l - LISP
       A - access/subscriber, a - Application route
       M - mobile route, r - RPL, t - Traffic Engineering, (!) - FRR Backup path
       s - local SRv6 route, z - local IID route

Gateway of last resort is not set

L    1.1.1.1/32 is directly connected, 00:08:25, Loopback0
O    2.2.2.2/32 [110/3] via 10.1.11.2, 00:02:26, HundredGigE0/0/0/0 (!)
                [110/2] via 10.1.33.2, 00:02:26, HundredGigE0/0/0/3
O    3.3.3.3/32 [110/2] via 10.1.11.2, 00:02:26, HundredGigE0/0/0/0
                [110/3] via 10.1.33.2, 00:02:26, HundredGigE0/0/0/3 (!)
O    4.4.4.4/32 [110/2] via 10.1.21.2, 00:02:26, HundredGigE0/0/0/1
                [110/3] via 10.1.33.2, 00:02:26, HundredGigE0/0/0/3 (!)
C    10.1.11.0/30 is directly connected, 04:31:47, HundredGigE0/0/0/0
L    10.1.11.1/32 is directly connected, 04:31:47, HundredGigE0/0/0/0
C    10.1.21.0/30 is directly connected, 04:31:47, HundredGigE0/0/0/1
L    10.1.21.1/32 is directly connected, 04:31:47, HundredGigE0/0/0/1
O    10.1.22.0/30 [110/2] via 10.1.21.2, 00:02:26, HundredGigE0/0/0/1
                  [110/2] via 10.1.33.2, 00:02:26, HundredGigE0/0/0/3
C    10.1.33.0/30 is directly connected, 04:31:47, HundredGigE0/0/0/3
L    10.1.33.1/32 is directly connected, 04:31:47, HundredGigE0/0/0/3
<snip>
```
> [!IMPORTANT]
> the ‘(!)’ at the end of some of the loopback routes.  These are the routes protected by FRR.  These routes are installed in the FIB as a backup route in the event the primary path fails.  With these backup routes, the router does not need to wait for OSPF to reconverge before forwarding packets again.


## Step 4 - Validate Segment Routing Labels

All Segment-Routing labels are stored in and advertised to other nodes by the IGP, in our case OSPF.  We can see the labels assigned and validate that SR is running by inspecting both the MPLS forwarding plane and the OSPF opaque database.   

On each router, inspect the MPLS forwarding table:


```bash
RP/0/RP0/CPU0:sr-p001# sh mpls forwarding

Local  Outgoing    Prefix             Outgoing     Next Hop        Bytes       
Label  Label       or ID              Interface                    Switched    
------ ----------- ------------------ ------------ --------------- ------------
16002  Pop         SR Pfx (idx 2)     Hu0/0/0/3    10.1.33.2       0           
       16002       SR Pfx (idx 2)     Hu0/0/0/0    10.1.11.2       0            (!)
16003  Pop         SR Pfx (idx 3)     Hu0/0/0/0    10.1.11.2       0           
       16003       SR Pfx (idx 3)     Hu0/0/0/3    10.1.33.2       0            (!)
16004  Pop         SR Pfx (idx 4)     Hu0/0/0/1    10.1.21.2       0           
       16004       SR Pfx (idx 4)     Hu0/0/0/3    10.1.33.2       0            (!)
24000  Pop         SR Adj (idx 0)     Hu0/0/0/1    10.1.21.2       0           
24001  Pop         SR Adj (idx 0)     Hu0/0/0/1    10.1.21.2       0           
       16004       SR Adj (idx 0)     Hu0/0/0/3    10.1.33.2       0            (!)
24002  Pop         SR Adj (idx 0)     Hu0/0/0/0    10.1.11.2       0           
24003  Pop         SR Adj (idx 0)     Hu0/0/0/0    10.1.11.2       0           
       16003       SR Adj (idx 0)     Hu0/0/0/3    10.1.33.2       0            (!)
24004  Pop         SR Adj (idx 0)     Hu0/0/0/3    10.1.33.2       0           
24005  Pop         SR Adj (idx 0)     Hu0/0/0/3    10.1.33.2       0           
       16002       SR Adj (idx 0)     Hu0/0/0/0    10.1.11.2       0            (!)
```

In the example output from sr-p001, we see the dynamic adjacency-sid labels assigned to the interfaces that are participating in MPLS forwarding below.  These dynamic labels are in the **24000** and up range. We enabled all interfaces for MPLS forwarding when we configured ‘segment-routing forwarding mpls’ at the global OSPF level then configured all interfaces in the area 0 sub-context.  We also see some adjacencies as protected with the ‘(!)’.  **These are built by FRR TI-LFA**.

```
16002  Pop         SR Pfx (idx 2)     Hu0/0/0/3    10.1.33.2       0           
       16002       SR Pfx (idx 2)     Hu0/0/0/0    10.1.11.2       0            (!)
16003  Pop         SR Pfx (idx 3)     Hu0/0/0/0    10.1.11.2       0           
       16003       SR Pfx (idx 3)     Hu0/0/0/3    10.1.33.2       0            (!)
16004  Pop         SR Pfx (idx 4)     Hu0/0/0/1    10.1.21.2       0           
       16004       SR Pfx (idx 4)     Hu0/0/0/3    10.1.33.2       0            (!)
```

In addition to the adjacency-sids, we also see the prefix-sids that we configured for interface loopback 0 in OSPF. These prefix-sids are highlighted at the top of the output.  You will see back up paths here as well with outgoing labels to complete the backup LSP.

<details><summary><font size=4> Expand for MPLS label table view </summary><pre><code></font>
 Another view of Segment Routing labels is in the MPLS Label Table, which is the database of all local labels created by the router, and how it knows them. Review each router’s label table:
 
 ```bash
 RP/0/RP0/CPU0:sr-p001#show mpls label table
Table Label   Owner                           State  Rewrite
----- ------- ------------------------------- ------ -------
0     0       LSD(A)                          InUse  Yes
0     1       LSD(A)                          InUse  Yes
0     2       LSD(A)                          InUse  Yes
0     13      LSD(A)                          InUse  Yes
0     16000   OSPF(A):ospf-1                  InUse  No
0     24000   OSPF(A):ospf-1                  InUse  Yes
0     24001   OSPF(A):ospf-1                  InUse  Yes
0     24002   OSPF(A):ospf-1                  InUse  Yes
0     24003   OSPF(A):ospf-1                  InUse  Yes
0     24004   OSPF(A):ospf-1                  InUse  Yes
0     24005   OSPF(A):ospf-1                  InUse  Yes
 What we are seeing here is the global SR label database starts at 16000, which is the default value.  Next, we see 24000, which is the start of the dynamic label database space.  Labels 24001-24005 are the dynamic labels that were automatically generated by the router’s segment routing process and the advertised via the IGP process, OSPF process 1.
 For even more detailed information of the Label Switch Database (LSD), check the output of ‘show mpls lsd forwarding details’.   
 ```
 > [!NOTE]
 >This command will deliver a lot of data that is outside the scope of this lab, but will give you extra information for future troubleshooting and understanding of the SR-MPLS forwarding plane.

 </pre></code></details> <br>

Let's investigate the OSPF SID databaset to ensure we can see our neighbors prefix-sid's for their loopbacks 
 
 ```bash
 RP/0/RP0/CPU0:sr-p001#show ospf sid-database
 
SID Database for ospf 1 with ID 1.1.1.1

SID          Prefix/Mask
--------     ------------------
1            1.1.1.1/32               (L)
2            2.2.2.2/32               
3            3.3.3.3/32               
4            4.4.4.4/32 
```

 As you can see from the output above, all SIDs we configured on all the routers are present in the OSPF sid-database. You should see similar output on all routers.
 
[Prev Task](../README.md) | [Next Task](../task2/task2.md) 
