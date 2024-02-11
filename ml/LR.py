from datetime import datetime
from matplotlib import pyplot as plt
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
# from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score

class AprendizajeAutomatico():

    def __init__(self):
        
        print("Cargando conjunto de datos ...")
        
        self.conjunto_datos_flujo = pd.read_csv('FlowStatsfile.csv')

        self.conjunto_datos_flujo.iloc[:, 2] = self.conjunto_datos_flujo.iloc[:, 2].str.replace('.', '')
        self.conjunto_datos_flujo.iloc[:, 3] = self.conjunto_datos_flujo.iloc[:, 3].str.replace('.', '')
        self.conjunto_datos_flujo.iloc[:, 5] = self.conjunto_datos_flujo.iloc[:, 5].str.replace('.', '')        

    def entrenamiento_flujo(self):

        print("Entrenamiento de Flujo ...")
        
        X_flujo = self.conjunto_datos_flujo.iloc[:, :-1].values
        X_flujo = X_flujo.astype('float64')

        y_flujo = self.conjunto_datos_flujo.iloc[:, -1].values

        X_flujo_entrenamiento, X_flujo_prueba, y_flujo_entrenamiento, y_flujo_prueba = train_test_split(X_flujo, y_flujo, test_size=0.25, random_state=0)

        clasificador = LogisticRegression(solver='liblinear', random_state=0)
        modelo_flujo = clasificador.fit(X_flujo_entrenamiento, y_flujo_entrenamiento)

        y_flujo_predicho = modelo_flujo.predict(X_flujo_prueba)

        print("------------------------------------------------------------------------------")

        print("matriz de confusión")
        mc = confusion_matrix(y_flujo_prueba, y_flujo_predicho)
        print(mc)

        acc = accuracy_score(y_flujo_prueba, y_flujo_predicho)

        print("exactitud de éxito = {0:.2f} %".format(acc*100))
        error = 1.0 - acc
        print("exactitud de fallo = {0:.2f} %".format(error*100))
        print("------------------------------------------------------------------------------")
        
        benin = 0
        ddos = 0
        for i in y_flujo:
            if i == 0:
                benin += 1
            elif i == 1:
                ddos += 1
                
        print("benin = ", benin)
        print("ddos = ", ddos)
        print("------------------------------------------------------------------------------")
        
        plt.title("Conjunto de Datos")
        plt.tight_layout()
        
        explode = [0, 0.1]
        
        plt.pie([benin,ddos], labels=['NORMAL','DDoS'], wedgeprops={'edgecolor':'black'}
                , explode=explode, autopct="%1.2f%%")
        plt.show()
        
        icmp = 0
        tcp = 0
        udp = 0
        
        proto = self.conjunto_datos_flujo.iloc[:, 7].values
        proto = proto.astype('int')
        for i in proto:
            if i == 6:
                tcp += 1
            elif i == 17:
                udp += 1
            elif i == 1:
                icmp += 1

        print("tcp = ", tcp)
        print("udp = ", udp)
        print("icmp = ", icmp)
        
        plt.title("Conjunto de Datos")
        
        explode = [0, 0.1, 0.1]
        
        plt.pie([icmp,tcp,udp], labels=['ICMP','TCP','UDP'], wedgeprops={'edgecolor':'black'}
                , explode=explode, autopct="%1.2f%%")
        plt.show()
        
        icmp_normal = 0
        tcp_normal = 0
        udp_normal = 0
        icmp_ddos = 0
        tcp_ddos = 0
        udp_ddos = 0
        
        proto = self.conjunto_datos_flujo.iloc[:, [7,-1]].values
        proto = proto.astype('int')
       
        for i in proto:
            if i[0] == 6 and i[1] == 0:
                tcp_normal += 1
            elif i[0] == 6 and i[1] == 1:
                tcp_ddos += 1
            
            if i[0] == 17 and i[1] == 0:
                udp_normal += 1
            elif i[0] == 17 and i[1] == 1:
                udp_ddos += 1
            
            if i[0] == 1 and i[1] == 0:
                icmp_normal += 1
            elif i[0] == 1 and i[1] == 1:
                icmp_ddos += 1

        print("tcp_normal = ", tcp_normal)
        print("tcp_ddos = ", tcp_ddos)
        print("udp_normal = ", udp_normal)
        print("udp_ddos = ", udp_ddos)
        print("icmp_normal = ", icmp_normal)
        print("icmp_ddos = ", icmp_ddos)
        
        plt.title("Conjunto de Datos")
        
        explode = [0, 0.1, 0.1, 0.1, 0.1, 0.1]
        
        plt.pie([icmp_normal,icmp_ddos,tcp_normal,tcp_ddos,udp_normal,udp_ddos], 
                labels=['ICMP_Normal','ICMP_DDoS','TCP_Normal','TCP_DDoS','UDP_Normal','UDP_DDoS'], 
                wedgeprops={'edgecolor':'black'}, explode=explode, autopct="%1.2f%%")
        plt.show()
        
def main():
    start = datetime.now()
    
    aa = AprendizajeAutomatico()
    aa.entrenamiento_flujo()

    end = datetime.now()
    print("Tiempo de entrenamiento: ", (end-start)) 

if __name__ == "__main__":
    main()
