# cloudlab_e2e_topology
5G Wireless network experiment on POWDER platform. 

A general question might be whether a delay emulation is needed here given the wireless nature. without a delay might actually help us see everything better and clearer.


### Notes
set up the routing at the dualq node:
```bash
sudo ip route add 12.1.1.64/26 via 10.0.1.1
sudo ip route add 12.1.1.128/25 via 10.0.1.1
```

at the node rx0:
```bash
sudo iptables -P FORWARD ACCEPT

sudo ip route add 12.1.1.64/26 via 192.168.70.140

sudo ip route add 12.1.1.128/25 via 192.168.70.134
```


change to prague:
```bash
sudo sysctl -w net.ipv4.tcp_congestion_control=prague
sudo sysctl -w net.ipv4.tcp_ecn=3
```

change to cubic:
```bash
sudo sysctl -w net.ipv4.tcp_congestion_control=cubic
sudo sysctl -w net.ipv4.tcp_ecn=0
```

check the CC and ECN status
```bash
sudo sysctl net.ipv4.tcp_congestion_control
sudo sysctl net.ipv4.tcp_ecn
```


build OAI without overwriting the previous build:
1. modify the build_oai script to designate another build directory. 
2. do not use the -c -C flag
