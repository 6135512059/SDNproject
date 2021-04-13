#!/usr/bin/python
"""
Script modified by KULJAREE - Visual Network Description (SDN version)
It setup the network topology. Also there is a mobility function for moving
Node
We move a host from s1 (MAG1) to s2 (MAG2),
and then back to s1.
Gotchas:
1. The interfaces are not renamed; this
means that s1-eth1 will show up on other
switches.
2. The reference controller doesn't support
mobility, so we need to flush the switch
flow tables.
3. The port numbers reported by the switch
may not match the actual OpenFlow port
numbers used by OVS.
Good luck!
"""
from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSSwitch, OVSKernelSwitch, UserSwitch
from mininet.topo import LinearTopo
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import Link, TCLink
from mininet.util import dumpNetConnections
from time import sleep
import os
def printConnections( switches ):
    "Compactly print connected nodes to each switch"
    for sw in switches:
        print '%s:' % sw,
        for intf in sw.intfList():
            link = intf.link
            if link:
               intfs = [ link.intf1, link.intf2 ]
               if intfs[ 0 ].node != sw:
                  intfs.reverse()
               local, remote = intfs
               print remote.node,
        print
class RYUBridge( Controller ):
    "Custom Controller class to invoke my RYU simple_switch_13"
    def start( self ):
        "Start RYU learning switch"
        self.ryu = '%s/ryu/bin/ryu-manager' % os.environ[ 'HOME' ]
        self.cmd( self.ryu, 'simple_switch_13_my.py &' )
    def stop( self ):
        "Stop RYU"
        self.cmd( 'kill %' + self.ryu )
controllers = { 'ryubridge': RYUBridge}
def topology():
    "Create a network."
    net = Mininet( controller=RYUBridge, link=TCLink, switch = MobilitySwitch )
#    print " --------------- 6135512059 TEST --------"
#    print " *** Create Ruy Controller ***"
        #Add Controller
    c1 = net.addController( 'c1', controller=RYUBridge, ip='::1', port=6633 )
#            print " **** Create Switchs **** "
    #Add SwitchsFFF
    s1 = net.addSwitch( 's1',switch=UserSwitch, mac='00:00:00:11:00:00' )
    s2 = net.addSwitch( 's2', switch=UserSwitch, mac='00:00:00:22:00:00' )
    s3 = net.addSwitch( 's3', switch=UserSwitch, mac='00:00:00:33:00:00' )
    # Create Linux Router
    LMA1 = net.addHost( 'LMA1', mac='00:00:00:00:22:00')
    MAG1 = net.addHost( 'MAG1', mac='00:00:00:00:33:00')
    MAG2 = net.addHost( 'MAG2', mac='00:00:00:00:44:00')
#    print " **** Create Hosts **** "
    #Add Hosts
    MN = net.addHost('MN', mac = '00:00:00:00:00:11')
    CN = net.addHost('CN', mac = '00:00:00:00:00:22')
    h2 = net.addHost('h2', mac = '00:00:00:00:00:33')
    #Create Links
 #   print "*** Creating links"
    net.addLink( s1, LMA1, 1, 0, bw=10 )
    net.addLink( s1, MAG1, 2, 0, bw=10 )
    net.addLink( s1, MAG2, 3, 0, bw=10 )
    net.addLink( LMA1, CN, 1, 0, bw=10 )
    net.addLink( MAG1, s2, 1, 1, bw=10 )
    net.addLink( s2, MN, 2, 0, bw=10 )
    net.addLink( MAG2, s3, 1, 1, bw=10 )
    net.addLink( s3, h2, 2, 0, bw=10 )
  #  print "*** Starting network"
    net.build()
    s1.start( [c1] )
    s2.start( [c1] )
    s3.start( [c1] )
    c1.start()
    #Create Links
   # print "*** Creating links"
    net.addLink( s1, LMA1, 1, 0, bw=10 )
    net.addLink( s1, MAG1, 2, 0, bw=10 )
    net.addLink( s1, MAG2, 3, 0, bw=10 )
    net.addLink( LMA1, CN, 1, 0, bw=10 )
    net.addLink( MAG1, s2, 1, 1, bw=10 )
    net.addLink( s2, MN, 2, 0, bw=10 )
    net.addLink( MAG2, s3, 1, 1, bw=10 )
    net.addLink( s3, h2, 2, 0, bw=10 )
   # print "*** Starting network"
    net.build()
    s1.start( [c1] )
    s2.start( [c1] )
    s3.start( [c1] )
    c1.start()
    print MAG2.cmd( 'ifconfig MAG2-eth1 inet6 add 2001:1::2/64' )
    print CN.cmd( 'ifconfig CN-eth0 inet6 add 2001:2::2/64' )
    print CN.cmd( 'ip -6 route add ::/0 via 2001:2::1' )
    print LMA1.cmd( 'sysctl -w net.ipv6.conf.all.forwarding=1' )
    print MAG1.cmd( 'sysctl -w net.ipv6.conf.all.forwarding=1' )
    print MAG2.cmd( 'sysctl -w net.ipv6.conf.all.forwarding=1' )
    # Add rounting
    print LMA1.cmd( 'ip -6 route add ::/0 via 2001:100::2' )
    print MAG1.cmd( 'ip -6 route add ::/0 via 2001:100::1' )
    print MAG2.cmd( 'ip -6 route add ::/0 via 2001:100::1' )
    print
    print '* Starting network:'
    printConnections( net.switches )
    print '*Identifying switch interface for MN'
    MN, s2 = net.get( 'MN', 's2' )
    hintf, sintf = MN.connectionsTo( s2 )[0]
    last = s2
    print "*** Running CLI"
    CLI( net ) #for start PMIPv6 Service /SDN-Mobility Service
    # Simple test of mobility
    print
    for s in 3, 2, 3, 2, 3: #sw2-->sw3-->sw2
        next = net['s%d' % s ]
        print '* Moving', sintf, 'from', last, 'to', next
        last.detach( sintf )
        last.delIntf( sintf )
        next.attach( sintf )
        next.addIntf( sintf )
        sintf.node = next
        print '* Clearing out old flows'
        for sw in net.switches:
            sw.dpctl( 'del-flows' )
        print '* New network:'
        print MN.cmd( 'ifconfig MN-eth0 down' )
        print MN.cmd( 'ifconfig MN-eth0 up' )
        printConnections( net.switches )
        last = next
        #end moving code
        CLI ( net )
    CLI (net)
    net.stop()
if __name__ == '__main__':
    setLogLevel( 'info' )
    topology()
topos = { 'mytopo': ( lambda: topology() ) }




