from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.node import OVSKernelSwitch, RemoteController
from time import sleep
from datetime import datetime
from random import randrange, choice

class MyTopo(Topo):
    def build(self):
        switches = []
        hosts = []

        for i in range(1, 7):
            switch_name = 's{}'.format(i)
            switches.append(self.addSwitch(switch_name, cls=OVSKernelSwitch, protocols='OpenFlow13'))

            for j in range(1, 4):
                host_name = 'h{}'.format((i-1)*3 + j)
                ip = '10.0.0.{}/24'.format((i-1)*3 + j)
                host = self.addHost(host_name, cpu=1.0/20, mac='00:00:00:00:00:{:02d}'.format((i-1)*3 + j), ip=ip)
                hosts.append(host)
                self.addLink(host, switches[-1])

            if i > 1:
                self.addLink(switches[-2], switches[-1])

def ip_generator():
    ip = '10.0.0.{}'.format(randrange(1, 19))
    return ip

def startNetwork():
    topo = MyTopo()
    c0 = RemoteController('c0', ip='192.168.4.100', port=6653)
    net = Mininet(topo=topo, link=TCLink, controller=c0)
    net.start()

    hosts = net.hosts
    print("--------------------------------------------------------------------------------")    
    print("Generando tráfico ...")    

    h1 = net.get('h1')
    h1.cmd('cd /home/mininet/webserver')
    h1.cmd('python -m SimpleHTTPServer 80 &')
    h1.cmd('iperf -s -p 5050 &')
    h1.cmd('iperf -s -u -p 5051 &')

    for h in hosts:
        h.cmd('cd /home/mininet/Downloads')

    for i in range(600):
        print("--------------------------------------------------------------------------------")    
        print("Iteración n {} ...".format(i+1))
        print("--------------------------------------------------------------------------------") 

        for _ in range(10):
            src = choice(hosts)
            dst = ip_generator()

            src.cmd("ping {} -c 100 &".format(dst))
            src.cmd("iperf -p 5050 -c 10.0.0.1")
            src.cmd("iperf -p 5051 -u -c 10.0.0.1")

            print("{} Descargando index.html de h1".format(src))
            src.cmd("wget http://10.0.0.1/index.html")
            print("{} Descargando test.zip de h1".format(src))
            src.cmd("wget http://10.0.0.1/test.zip")

        h1.cmd("rm -f *.* /home/mininet/Downloads")

    print("--------------------------------------------------------------------------------")  

    net.stop()

if __name__ == '__main__':
    start = datetime.now()
    setLogLevel('info')
    startNetwork()
    end = datetime.now()

    print(end-start)
