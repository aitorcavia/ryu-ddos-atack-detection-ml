from datetime import datetime
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import confusion_matrix, accuracy_score

class AprendizajeAutomatico:

    def __init__(self):
        print("Cargando conjunto de datos ...")
        self.conjunto_datos = pd.read_csv('FlowStatsfile.csv')
        self.conjunto_datos.iloc[:, 2] = self.conjunto_datos.iloc[:, 2].str.replace('.', '')
        self.conjunto_datos.iloc[:, 3] = self.conjunto_datos.iloc[:, 3].str.replace('.', '')
        self.conjunto_datos.iloc[:, 5] = self.conjunto_datos.iloc[:, 5].str.replace('.', '')   

    def entrenamiento_flujo(self):
        print("Entrenando el flujo...")
        X_flujo = self.conjunto_datos.iloc[:, :-1].values
        X_flujo = X_flujo.astype('float64')
        y_flujo = self.conjunto_datos.iloc[:, -1].values
        X_flujo_entrenamiento, X_flujo_prueba, y_flujo_entrenamiento, y_flujo_prueba = train_test_split(X_flujo, y_flujo, test_size=0.25, random_state=0)
        clasificador = GaussianNB()
        modelo_flujo = clasificador.fit(X_flujo_entrenamiento, y_flujo_entrenamiento)
        y_flujo_predicho = modelo_flujo.predict(X_flujo_prueba)
        print("------------------------------------------------------------------------------")
        print("Matriz de confusión:")
        cm = confusion_matrix(y_flujo_prueba, y_flujo_predicho)
        print(cm)
        acc = accuracy_score(y_flujo_prueba, y_flujo_predicho)
        print("Precisión de éxito = {0:.2f} %".format(acc*100))
        fallo = 1.0 - acc
        print("Precisión de fallo = {0:.2f} %".format(fallo*100))
        print("------------------------------------------------------------------------------")
        etiquetas = ['TP','FP','FN','TN']
        plt.title("Naive Bayes")
        plt.xlabel('Clase predicha')
        plt.ylabel('Número de flujos')
        plt.tight_layout()
        plt.style.use("seaborn-darkgrid")
        valores = [cm[0][0],cm[0][1],cm[1][0],cm[1][1]]
        plt.bar(etiquetas, valores, color="#0000ff", label='NB')
        plt.legend()
        plt.show()

def principal():
    inicio = datetime.now()
    ml = AprendizajeAutomatico()
    ml.entrenamiento_flujo()
    fin = datetime.now()
    print("Tiempo de entrenamiento: ", (fin-inicio)) 

if __name__ == "__main__":
    principal()
