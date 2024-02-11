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
        # Crear los switches s1-s6
        switches = []
        for i in range(1, 7):
            switch_name = 's{}'.format(i)
            switches.append(self.addSwitch(switch_name, cls=OVSKernelSwitch, protocols='OpenFlow13'))

        # Crear los hosts h1-h18 y añadirlos a los switches correspondientes
        for i in range(1, 19):
            host_name = 'h{}'.format(i)
            host_ip = '10.0.0.{}/24'.format(i)
            switch_index = (i - 1) // 3
            switches[switch_index].addHost(host_name, cpu=1.0/20, mac="00:00:00:00:00:{:02d}".format(i), ip=host_ip)

        # Conectar los hosts a los switches
        for i in range(1, 7):
            for j in range(3):
                self.addLink('h{}'.format((i-1)*3 + j + 1), 's{}'.format(i))

        # Conectar los switches entre sí
        for i in range(1, 6):
            self.addLink('s{}'.format(i), 's{}'.format(i + 1))

def ip_generator():
    ip = "10.0.0.{}".format(randrange(1, 19))
    return ip

def startNetwork():
    topo = MyTopo()
    c0 = RemoteController('c0', ip='192.168.4.100', port=6653)
    net = Mininet(topo=topo, link=TCLink, controller=c0)
    net.start()

    hosts = net.hosts
    print("--------------------------------------------------------------------------------")    
    print("Generando tráfico ...")    

    # Configurar el servidor web en h1
    h1 = net.get('h1')
    h1.cmd('cd /home/mininet/webserver')
    h1.cmd('python -m SimpleHTTPServer 80 &')

    # Realizar ataques desde hosts aleatorios
    for _ in range(4):
        src = choice(hosts)
        dst = ip_generator()

        print("--------------------------------------------------------------------------------")
        print("Ejecutando ataque ICMP (Ping) Flood")
        print("--------------------------------------------------------------------------------")
        src.cmd("timeout 20s hping3 -1 -V -d 120 -w 64 -p 80 --rand-source --flood {}".format(dst))
        sleep(100)

        print("--------------------------------------------------------------------------------")
        print("Ejecutando ataque UDP Flood")
        print("--------------------------------------------------------------------------------")
        src.cmd("timeout 20s hping3 -2 -V -d 120 -w 64 --rand-source --flood {}".format(dst))
        sleep(100)

        print("--------------------------------------------------------------------------------")
        print("Ejecutando ataque TCP-SYN Flood")
        print("--------------------------------------------------------------------------------")
        src.cmd('timeout 20s hping3 -S -V -d 120 -w 64 -p 80 --rand-source --flood 10.0.0.1')
        sleep(100)

        print("--------------------------------------------------------------------------------")
        print("Ejecutando ataque LAND Attack")
        print("--------------------------------------------------------------------------------")
        src.cmd("timeout 20s hping3 -1 -V -d 120 -w 64 --flood -a {} {}".format(dst, dst))
        sleep(100)
        print("--------------------------------------------------------------------------------")

    net.stop()

if __name__ == '__main__':
    start = datetime.now()
    setLogLevel('info')
    startNetwork()
    end = datetime.now()

    print(end - start)
