from datetime import datetime
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix, accuracy_score

class MachineLearning:

    def __init__(self):
        # Carga del conjunto de datos
        print("Cargando dataset ...")
        self.flow_dataset = pd.read_csv('FlowStatsfile.csv')

        # Eliminación de puntos en los datos numéricos
        self.flow_dataset.iloc[:, 2] = self.flow_dataset.iloc[:, 2].str.replace('.', '')
        self.flow_dataset.iloc[:, 3] = self.flow_dataset.iloc[:, 3].str.replace('.', '')
        self.flow_dataset.iloc[:, 5] = self.flow_dataset.iloc[:, 5].str.replace('.', '')   

    def flow_training(self):
        # Entrenamiento del flujo
        print("Entrenando flujo ...")
        
        # Separación de características y etiquetas
        X_flow = self.flow_dataset.iloc[:, :-1].values
        X_flow = X_flow.astype('float64')
        y_flow = self.flow_dataset.iloc[:, -1].values

        # División en conjuntos de entrenamiento y prueba
        X_flow_train, X_flow_test, y_flow_train, y_flow_test = train_test_split(X_flow, y_flow, test_size=0.25, random_state=0)

        # Inicialización del clasificador SVC
        classifier = SVC(kernel='rbf', random_state=0)
        flow_model = classifier.fit(X_flow_train, y_flow_train)

        # Predicción sobre el conjunto de prueba
        y_flow_pred = flow_model.predict(X_flow_test)

        print("------------------------------------------------------------------------------")

        # Cálculo de la matriz de confusión
        print("Matriz de confusión:")
        cm = confusion_matrix(y_flow_test, y_flow_pred)
        print(cm)

        # Cálculo de la precisión
        acc = accuracy_score(y_flow_test, y_flow_pred)
        print("Precisión de éxito = {0:.2f} %".format(acc*100))
        fail = 1.0 - acc
        print("Precisión de fallo = {0:.2f} %".format(fail*100))
        print("------------------------------------------------------------------------------")
    
def main():
    start = datetime.now()
    
    ml = MachineLearning()
    ml.flow_training()

    end = datetime.now()
    print("Tiempo de entrenamiento: ", (end-start)) 

if __name__ == "__main__":
    main()
