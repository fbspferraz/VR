from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import RemoteController
from mininet.node import OVSSwitch
from mininet.cli import CLI
from mininet.log import info
from mininet.log import setLogLevel
from mininet.link import TCLink
from subprocess import call



    #"Topology Exercise 2"

def Topology():
    #"Create custom topo."

    info('\nNet 1 -> 192.168.10.0/24\nNet 2 -> 192.168.20.0/24\nNet 3 -> 192.168.30.0/24\n')

    net = Mininet( controller=RemoteController, link=TCLink, switch=OVSSwitch )

    info('***Creating remote controller on port 6633 (L2 switches)\n')
    c0 = net.addController(name='c0',
                        controller=RemoteController,
                        ip='127.0.0.1',
                        protocol='tcp',
                        port=6633)
    
    info('***Creating remote controller on port 6653 (L3 switch)\n')
    c1 = net.addController(name='c1',
                        controller=RemoteController,
                        ip='127.0.0.1',
                        protocol='tcp',
                        port=6653)

    info('Adding L3 switch\n')
    r1 = net.addSwitch('r1', cls = OVSSwitch, dpid = '0000000000000001')  # L3 switch

    info('Adding L2 switches\n')
    s1 = net.addSwitch('s1', cls=OVSSwitch, dpid='0000000000000002') # L2 Switch Net 1 (no ip)
    s2 = net.addSwitch('s2', cls=OVSSwitch, dpid='0000000000000003') # L2 Switch Net 2 (no ip)
    s3 = net.addSwitch('s3', cls=OVSSwitch, dpid='0000000000000004') # L2 Switch Net 3 (no ip)


    info('Add hosts and switches\n')
    h1_1 = net.addHost( 'h1_1', ip = '192.168.10.1/24', mac = '00:00:00:00:00:01', defaultRoute='via 192.168.10.254' )   # Host 1 Net A
    h1_2 = net.addHost( 'h1_2', ip = '192.168.10.2/24', mac = '00:00:00:00:00:02', defaultRoute='via 192.168.10.254' )   # Host 2 Net A
    h1_3 = net.addHost( 'h1_3', ip = '192.168.10.3/24', mac = '00:00:00:00:00:03', defaultRoute='via 192.168.10.254' )   # Host 3 Net A
    h2_1 = net.addHost( 'h2_1', ip = '192.168.20.1/24', mac = '00:00:00:00:00:04', defaultRoute='via 192.168.20.254' )   # Host 1 Net B
    h2_2 = net.addHost( 'h2_2', ip = '192.168.20.2/24', mac = '00:00:00:00:00:05', defaultRoute='via 192.168.20.254' )   # Host 2 Net B
    h2_3 = net.addHost( 'h2_3', ip = '192.168.20.3/24', mac = '00:00:00:00:00:06', defaultRoute='via 192.168.20.254' )   # Host 3 Net B
    h3_1 = net.addHost( 'h3_1', ip = '192.168.30.1/24', mac = '00:00:00:00:00:07', defaultRoute='via 192.168.30.254' )   # Host 1 Net C
    h3_2 = net.addHost( 'h3_2', ip = '192.168.30.2/24', mac = '00:00:00:00:00:08', defaultRoute='via 192.168.30.254' )   # Host 2 Net C
    h3_3 = net.addHost( 'h3_3', ip = '192.168.30.3/24', mac = '00:00:00:00:00:09', defaultRoute='via 192.168.30.254' )   # Host 3 Net C
    
    info('Adding links Net 1\n')
    net.addLink( h1_1, s1 )
    net.addLink( h1_2, s1 )
    net.addLink( h1_3, s1 )
    net.addLink( r1, s1, cls=TCLink, delay = '5ms' )

    info('\nAdding links Net 2\n')
    net.addLink( h2_1, s2 )
    net.addLink( h2_2, s2 )
    net.addLink( h2_3, s2, cls=TCLink, delay = '5ms' )
    net.addLink( r1, s2 )

    info('\nAdding links Net 3\n')
    net.addLink( h3_1, s3 )
    net.addLink( h3_2, s3 )
    net.addLink( h3_3, s3, cls=TCLink, losses = '10')
    net.addLink( r1, s3 )

    info('Setting MAC addresses to switches')
    s1.setMAC('10:00:00:00:00:01', 's1-eth1')
    s1.setMAC('10:00:00:00:00:02', 's1-eth2')
    s1.setMAC('10:00:00:00:00:03', 's1-eth3')
    s1.setMAC('10:00:00:00:00:04', 's1-eth4')
    s2.setMAC('20:00:00:00:00:01', 's2-eth1')
    s2.setMAC('20:00:00:00:00:02', 's2-eth2')
    s2.setMAC('20:00:00:00:00:03', 's2-eth3')
    s2.setMAC('20:00:00:00:00:04', 's2-eth4')
    s3.setMAC('30:00:00:00:00:01', 's3-eth1')
    s3.setMAC('30:00:00:00:00:02', 's3-eth2')
    s3.setMAC('30:00:00:00:00:03', 's3-eth3')
    s3.setMAC('30:00:00:00:00:04', 's3-eth4')
    r1.setMAC('40:00:00:00:00:01', 'r1-eth1')
    r1.setMAC('40:00:00:00:00:02', 'r1-eth2')
    r1.setMAC('40:00:00:00:00:03', 'r1-eth3')


    net.build()

    # Switches
    r1.start([c1])
    s1.start([c0])
    s2.start([c0])
    s3.start([c0])

    info('\nSetting up of IP addresses in the R1\n')
    r1.cmd("ifconfig r1-eth1 0")
    r1.cmd("ifconfig r1-eth2 0")
    r1.cmd("ifconfig r1-eth3 0")  #limpar configuracao da interface
    r1.cmd("ip addr add 192.168.10.254/24 brd + dev r1-eth1")
    r1.cmd("ip addr add 192.168.20.254/24 brd + dev r1-eth2")
    r1.cmd("ip addr add 192.168.30.254/24 brd + dev r1-eth3")
    r1.cmd("echo 1 > /proc/sys/net/ipv4/ip_forward")

    info('Setting GW to hosts\n')
    h1_1.cmd("ip route add default via 192.168.10.254")  # GW Net A
    h1_2.cmd("ip route add default via 192.168.10.254")  # GW Net A
    h1_3.cmd("ip route add default via 192.168.10.254")  # GW Net A
    h2_1.cmd("ip route add default via 192.168.20.254")  # GW Net B
    h2_2.cmd("ip route add default via 192.168.20.254")  # GW Net B
    h2_3.cmd("ip route add default via 192.168.20.254")  # GW Net B
    h3_1.cmd("ip route add default via 192.168.30.254")  # GW Net B
    h3_2.cmd("ip route add default via 192.168.30.254")  # GW Net B
    h3_3.cmd("ip route add default via 192.168.30.254")  # GW Net B

    info('GW Net 1-> 192.168.10.254/24\nGW Net 2 -> 192.168.20.254/24\nGW Net 3 -> 192.168.30.254/24\n')
    #info('sudo mn --controller=remote,ip=127.0.0.1,port=6655\n')
    #info('sudo mn --controller=remote,ip=127.0.0.1,port=6633\n')
        
    # Start command line
    CLI(net)

    # Stop Network
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    Topology()
