from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.node import OVSKernelSwitch, RemoteController

class MyTopo(Topo):
    def build(self):
        # Crear switches s1-s6
        switches = [self.addSwitch('s{}'.format(i), cls=OVSKernelSwitch, protocols='OpenFlow13') for i in range(1, 7)]

        # Crear hosts h1-h18 y conectarlos a los switches correspondientes
        hosts = [self.addHost('h{}'.format(i), cpu=1.0/20, mac="00:00:00:00:00:{:02d}".format(i), ip="10.0.0.{}/24".format(i)) for i in range(1, 19)]
        for i, host in enumerate(hosts):
            switch_index = i // 3
            self.addLink(host, switches[switch_index])

        # Conectar los switches entre sí
        for i in range(1, 6):
            self.addLink('s{}'.format(i), 's{}'.format(i + 1))

def startNetwork():
    topo = MyTopo()
    c0 = RemoteController('c0', ip='192.168.4.100', port=6653)
    net = Mininet(topo=topo, link=TCLink, controller=c0)

    net.start()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    startNetwork()
