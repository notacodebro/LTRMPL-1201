# EVPN Route Type (RT) Table

| Route Type | Name | Usage |
|------------|----------------------------------|--------------------------------------------------------------------------------------------|
| 1 | Ethernet Auto-Discovery (AD) Route | Few routes sent per Ethernet Segment (ES), carries the list of EVIs that belong to ES. Used for mass withdrawal of MAC addresses, aliasing for load balancing, and split-horizon filtering. |
| 2 | MAC/IP Advertisement Route | Advertise MAC and IP address reachability, advertise IP/MAC binding. Provides MAC/IP bindings for ARP suppression and reduces unknown unicast flooding. |
| 3 | Inclusive Multicast Ethernet Tag Route | Multicast tunnel endpoint discovery. Establishes connection for broadcast, unknown unicast, and multicast (BUM) traffic from source PE to remote PE. Advertised per VLAN and per ESI basis. |
| 4 | Ethernet Segment Route | Redundancy group discovery, Designated Forwarder (DF) election. Enables discovery of connected PE devices on the same Ethernet segment. Supports multi-homing. |
| 5 | IP Prefix Route | Advertise IP prefixes independently of MAC routes. Used for inter-subnet forwarding. With EVPN IRB, host route /32 is advertised using RT-2 and subnet /24 using RT-5. |
| 6 | SMET/IGMP-MLD Proxy | Distributes explicit interest of a host or VM in receiving multicast group traffic, allowing selective forwarding and avoiding unnecessary flooding. |
| 7 | IGMP/MLD Join Sync | Synchronizes IGMP/MLD join states between Ethernet segment switches in multihoming scenarios for seamless failover. |
| 8 | IGMP/MLD Leave Sync | Synchronizes IGMP/MLD leave messages between Ethernet segment switches to prune multicast forwarding trees efficiently. |