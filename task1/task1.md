# Configure OSPF for the Underlay 

 The routers in the network have IP connectivity established between each other, but no routing protocols.  Since we will be using Segment Routing, we need to use a routing protocol that has been **extended** to support SR. OSPF and IS-IS have these extensions. In this task you will configure OSPF between all transport network routers, add Segent Rotuing and validate all configuratons through various show commands.

```
The transport network consists of four routers:

sr-p001
sr-p002
sr-pe001
sr-pe002
```

> [!IMPORTANT] 
> Changes made in IOS-XR  do not take affect until they have been committed.  If the changes configured are not possible to be committed due to an error, none of the changes will be committed until the error has been fixed.  To commit a configuration, simply type ‘commit’.  To view the reason for an erroneous commit, type ‘commit show’. 


## Step 1 - Configure the OSPF Process

IOS-XR configures its services and protocols at the process level.  For example, all OSPF configurations occur within the ‘router ospf’ process.   Bridge domains and virtual cross connects are configured under ‘l2vpn’.  This is important as we move forward as other operating systems that you may be familiar with may be different and allow you to configure these items under their respective interfaces.

1. Configure OSPF process '1'

``` bash 
#configure
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

<details><summary><font size=4> Expand for FRR and TI-LFA Details  </summary><pre><code></font>
Under the global configuration OSPF we configure context, enable the fast-reroute (FRR) and topology-independent loop free alternate (TI-LFA).  By enabling it at the global OSPF context, it turns the feature on for all areas and interfaces that are using the OSPF protocol.  You may also turn these on or off at the area or interface levels. <br>

For **FRR**, we have the option of using per-link or per-prefix FRR.  Per-link will create a single backup route for all routes on a specific egress link.  Per-prefix will create a backup route per route, regardless of egress link.  Per-prefix is more granular and flexible than per-link and is the recommended setting.<br>

**TI-LFA** builds a backup, loop-free labeled path to a destination prefix via an optimal routed path. This backup path is used by a transit node until the IGP finishes converging.<br>

Since our links are all point to point links, we can take advantage of OSPF’s point to point network type at the global OSPF process context as well.<br>

The last two items we need to configure in the global OSPF context before we begin configuring our Area 0 is the Segment Routing control and dataplanes.<br>
</pre></code></details>  


## Step 2 - Add Loopbacks, Configure Area backbone area


## Step 3 - Validate OSPF