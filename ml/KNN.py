from datetime import datetime
from matplotlib import pyplot as plt
import pandas as pd
from sklearn.model_selection import train_test_split
# from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
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

        clasificador = KNeighborsClassifier(n_neighbors=5, metric='minkowski', p=2)
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
        
        x = ['TP','FP','FN','TN']
        plt.title("KNN")
        plt.xlabel('Clase predicha')
        plt.ylabel('Número de flujos')
        plt.tight_layout()
        plt.style.use("seaborn-darkgrid")
        y = [mc[0][0],mc[0][1],mc[1][0],mc[1][1]]
        plt.bar(x,y, color="#e46e6e", label='KNN')
        plt.legend()
        plt.show()
    
def main():
    start = datetime.now()
    
    aa = AprendizajeAutomatico()
    aa.entrenamiento_flujo()

    end = datetime.now()
    print("Tiempo de entrenamiento: ", (end-start)) 

if __name__ == "__main__":
    main()
