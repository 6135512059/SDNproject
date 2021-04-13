#!/usr/bin/python
'''  Topology
                  c1
                  v
                  |
          ------------------
          |       |        |
          |       |        |
          v       v        v 
h1 <---> s1 <---> s2 <---> s3 <---> r1
         |                 |
         |                 |
        ap1               ap2
'''    
'Example for Handover'

from mininet.net import Mininet
from mininet.node import Controller, OVSKernelAP, OVSKernelSwitch
from mininet.link import TCLink, Intf
from mininet.cli import CLI
from mininet.log import setLogLevel, info

def topology():

    "Create a network."
    net = Mininet(controller=Controller, link=TCLink, accessPoint=OVSKernelAP)

    #Adding Physical Interface
    info( 'Defining physical interface\n')
    intfName = 'eth1'

    print "*** Creating nodes"
    h1 = net.addHost("h1", mac='00:00:00:00:00:04', ip='10.0.0.5/8', position='260,200,0')
    r1 = net.addHost("r1", mac='00:00:00:00:01:00', ip='192.168.59.4/24', position='500,20,0')
    sta1 = net.addStation('sta1', mac='00:00:00:00:00:02', ip='192.168.59.2/24')
    sta2 = net.addStation('sta2', mac='00:00:00:00:00:03', ip='10.0.0.3/8')
    ap1 = net.addAccessPoint('ap1', ssid='ssid-ap1', mode='g', channel='1', range='170', position='0,1,0')
    ap2 = net.addAccessPoint('ap2', ssid='ssid-ap2', mode='g', channel='9', range='170', position='300,1,0')
#    ap3 = net.addAccessPoint('ap3', ssid='ssid-ap3', mode='g', channel='11', range='170', position='520,1,0')
    s1 = net.addSwitch('s1',ip = '10.0.0.1/8' ,position='260,0,0')
    s2 = net.addSwitch('s2',ip = '172.26.117.1/24', position='260,170,0')
    s3 = net.addSwitch('s3',ip = '192.168.59.1/24', position='260,340,0')
    c1 = net.addController('c1', controller=Controller)

    print "*** Configuring wifi nodes"
    net.configureWifiNodes()

    print "*** Creating links"
    net.addLink(ap1, s1)
    net.addLink(ap2 ,s3)
#    net.addLink(ap3, s1)
    net.addLink(h1, s1)
    net.addLink(s1, s2)
    net.addLink(s2, s3)
    net.addLink(s3, r1)

    info( 'Adding hardware interface', intfName, 'to switch', s2.name, '\n')
    _intf = Intf( intfName, node=s2 )

    """plotting graph"""
    net.plotGraph(min_x=-200, max_x=700, min_y=-200, max_y=200)

    net.startMobility(time=50)
    net.mobility(sta1, 'start', time=50, position='400,0,0') #-100,-50 test1
    net.mobility(sta2, 'start', time=50, position='-100,0,0')
#    net.mobility(h1 , 'start',time = 50 ,position ='0.110.0')
    net.mobility(sta1, 'stop', time=650, position='500,1,0')
    net.mobility(sta2, 'stop', time=650, position='500,-1,0')
    net.stopMobility(time=650)

    print "*** Starting network"
    net.build()
    c1.start()
    s1.start([c1])
    ap1.start([c1])
    ap2.start([c1])
#    ap3.start([c1])
    s2.start([c1])
    s3.start([c1])

   # ap3.start([c1])
    print s1.cmd('ovs-vsctl set bridge s1 protocols=OpenFlow13')
    print s1.cmd('ovs-ofctl -O OpenFlow13 add-flow s1 action=flood')
    print s2.cmd('ovs-vsctl set bridge s2 protocols=OpenFlow13')
    print s2.cmd('ovs-ofctl -O OpenFlow13 add-flow s2 action=flood')
    print r1.cmd('ifconfig r1-eth0 inet6 add 2001:aaaa::1/64')
    print r1.cmd('ifconfig r1-eth1 inet6 add 2001:bbbb::1/64')
    print r1.cmd('radvd -C radvd1.conf')
    print r1.cmd('sysctl -w net.ipv6.conf.all.forwarding=1')
    print h1.cmd('ifconfig h1-eth0 inet6 add 2001:bbbb::2/64')
    print h1.cmd('ip -6 route add ::/0 via 2001:bbbb::1')

    print "*** Running CLI"
    CLI(net)

    print "*** Stopping network"
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology()
