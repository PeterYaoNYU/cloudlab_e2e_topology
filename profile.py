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

# Node definitions
nodes = {
    "5g": request.RawPC("5g"),
    "fifo_deep": request.RawPC("fifo_deep"),
    "dualq": request.RawPC("dualq"),
    "classic_sender": request.RawPC("classic_sender"),
    "prague_sender": request.RawPC("prague_sender")
}

# Set hardware types and disk images
nodes["5g"].hardware_type = "d430"
nodes["5g"].disk_image = "urn:publicid:IDN+emulab.net+image+mww2023:oai-cn5g-rfsim"
add_install_services_5g(nodes["5g"])

for node_name in ["fifo_deep", "dualq", "classic_sender", "prague_sender"]:
    nodes[node_name].hardware_type = "d710"
    nodes[node_name].disk_image = 'urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU22-64-STD'
    add_install_services(nodes[node_name])

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
    ]}
]

# Create interfaces and links
for net in net_conf:
    link = request.Link(net["name"])
    link.routable = True
    for node_info in net["nodes"]:
        iface = nodes[node_info["name"]].addInterface('{0}-{1}'.format(net["name"], node_info["addr"]))
        iface.addAddress(pg.IPv4Address(node_info["addr"], net["subnet"]))
        iface.bandwidth = 1000000 # note that I am setting the link to 1 Gbps, which should be limited later by traffic control 
        link.addInterface(iface)

# Print the generated rspec
pc.printRequestRSpec(request)