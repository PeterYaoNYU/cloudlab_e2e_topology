# Import the Portal object.
import geni.portal as portal
# Import the ProtoGENI library.
import geni.rspec.pg as pg
# Import the Emulab specific extensions.
import geni.rspec.emulab as emulab

# Create a portal object.
pc = portal.Context()

# Create a Request object to start building the RSpec.
request = pc.makeRequestRSpec()

# Function to add services to install packages
def add_install_services(node):
    node.addService(pg.Execute('/bin/sh', 'sudo apt-get update'))
    node.addService(pg.Execute('/bin/sh', 'sudo apt-get install -y iperf3 net-tools moreutils'))

# Function to configure the 5g node with custom setup script
def add_install_services_5g(node):
    node.addService(pg.Execute('/bin/bash', '/local/repository/setup_5g.sh'))

# Function to enable IP forwarding
def enable_ip_forwarding(node):
    node.addService(pg.Execute(shell="/bin/sh", command="sudo sysctl -w net.ipv4.ip_forward=1"))
    node.addService(pg.Execute(shell="/bin/sh", command="sudo iptables -P FORWARD ACCEPT"))

# Function to add static routes
def add_static_routes(node, routes):
    for route in routes:
        node.addService(pg.Execute(shell="/bin/sh", command="sudo ip route add {0} via {1}".format(route['net'], route['via'])))

# Node definitions
nodes = {
    "5g": request.RawPC("5g"),
    "fifo_deep": request.RawPC("fifo_deep"),
    "dualq": request.RawPC("dualq"),
    "classic_sender": request.RawPC("classic_sender"),
    "prague_sender": request.RawPC("prague_sender"),
    "classic_receiver": request.XenVM("classic_receiver"),  # Changed to VM
    "prague_receiver": request.XenVM("prague_receiver")    # Changed to VM
}

# Set hardware types and disk images
nodes["5g"].hardware_type = "d430"
nodes["5g"].disk_image = 'urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU22-64-STD'

add_install_services_5g(nodes["5g"])

for node_name in ["fifo_deep", "dualq", "classic_sender", "prague_sender"]:
    nodes[node_name].hardware_type = "d710"
    nodes[node_name].disk_image = 'urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU22-64-STD'
    add_install_services(nodes[node_name])

# Configure VMs (classic_receiver and prague_receiver)
for vm_name in ["classic_receiver", "prague_receiver"]:
    nodes[vm_name].disk_image = 'urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU22-64-STD'
    add_install_services(nodes[vm_name])

# Enable IP forwarding on fifo_deep and dualq nodes
enable_ip_forwarding(nodes["fifo_deep"])
enable_ip_forwarding(nodes["dualq"])

# Network configuration
net_conf = [
    {"name": "net_5g_fifo", "subnet": "255.255.255.0", "nodes": [
        {"name": "5g", "addr": "10.0.0.1"},
        {"name": "fifo_deep", "addr": "10.0.0.2"}
    ]},
    {"name": "net_5g_dualq", "subnet": "255.255.255.0", "nodes": [
        {"name": "5g", "addr": "10.0.1.1"},
        {"name": "dualq", "addr": "10.0.1.2"}
    ]},
    {"name": "net_fifo_classic", "subnet": "255.255.255.0", "nodes": [
        {"name": "fifo_deep", "addr": "10.0.2.1"},
        {"name": "classic_sender", "addr": "10.0.2.2"}
    ]},
    {"name": "net_dualq_prague", "subnet": "255.255.255.0", "nodes": [
        {"name": "dualq", "addr": "10.0.3.1"},
        {"name": "prague_sender", "addr": "10.0.3.2"}
    ]},
    {"name": "net_classic_dualq", "subnet": "255.255.255.0", "nodes": [
        {"name": "classic_sender", "addr": "10.0.4.1"},
        {"name": "dualq", "addr": "10.0.4.2"}
    ]},
    {"name": "net_prague_fifo", "subnet": "255.255.255.0", "nodes": [
        {"name": "prague_sender", "addr": "10.0.5.1"},
        {"name": "fifo_deep", "addr": "10.0.5.2"}
    ]},
    # New networks for receivers
    {"name": "net_fifo_classic_receiver", "subnet": "255.255.255.0", "nodes": [
        {"name": "fifo_deep", "addr": "10.0.6.1"},
        {"name": "classic_receiver", "addr": "10.0.6.2"}
    ]},
    {"name": "net_fifo_prague_receiver", "subnet": "255.255.255.0", "nodes": [
        {"name": "fifo_deep", "addr": "10.0.7.1"},
        {"name": "prague_receiver", "addr": "10.0.7.2"}
    ]},
    {"name": "net_dualq_prague_receiver", "subnet": "255.255.255.0", "nodes": [
        {"name": "dualq", "addr": "10.0.8.1"},
        {"name": "prague_receiver", "addr": "10.0.8.2"}
    ]}
]

# Create interfaces and links
for net in net_conf:
    link = request.Link(net["name"])
    link.routable = True
    for node_info in net["nodes"]:
        iface = nodes[node_info["name"]].addInterface('{0}-{1}'.format(net["name"], node_info["addr"]))
        iface.addAddress(pg.IPv4Address(node_info["addr"], net["subnet"]))
        iface.bandwidth = 1000000  # Set link to 1 Gbps
        link.addInterface(iface)

# Add static routes for classic_sender and classic_receiver
add_static_routes(nodes["classic_sender"], [
    {"net": "10.0.6.0/24", "via": "10.0.2.1"}  # Route to classic_receiver via fifo_deep
])

add_static_routes(nodes["classic_receiver"], [
    {"net": "10.0.2.0/24", "via": "10.0.6.1"}  # Route to classic_sender via fifo_deep
])

# Add static routes for prague_sender and prague_receiver
add_static_routes(nodes["prague_sender"], [
    {"net": "10.0.8.0/24", "via": "10.0.3.1"}  # Route to prague_receiver via dualq
])

add_static_routes(nodes["prague_receiver"], [
    {"net": "10.0.3.0/24", "via": "10.0.8.1"}  # Route to prague_sender via dualq
])

# Print the generated rspec
pc.printRequestRSpec(request)
