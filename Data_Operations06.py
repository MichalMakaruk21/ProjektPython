import pandas as pd
import numpy as np
import sklearn
from sklearn import linear_model
import matplotlib.pyplot as pyplot
import pickle
from matplotlib import style

df0 = pd.read_csv('PetrolData.csv', decimal=',', sep=';') #pobranie danych z pliku

df0['WeekDay'] = pd.to_datetime(df0['Date'], format="%d.%m.%Y").dt.dayofweek #konwersja stringa z datą na dzień tygodnia(zwraca w cyfrach 0-6)

df1 = df0.loc[:, ['WeekDay', 'Province', 'Company', 'Fuel', 'Prize']] #nowy dataframe bez danych adresowych

df1['WeekDay'] = np.where(df1['WeekDay'] == 0, 'Monday',    #Konwersja numeru dnia tygodnia na nazwę dnia tygodnia
                              np.where(df1['WeekDay'] == 1, 'Tuesday',
                                        np.where(df1['WeekDay'] == 2, 'Wednesday',
                                                 np.where(df1['WeekDay'] == 3,'Thursday',
                                                          np.where(df1['WeekDay'] == 4, 'Friday',
                                                                   np.where(df1['WeekDay'] == 5, 'Saturday', 'Sunday'))))))

df2 = pd.get_dummies(df1)#Nowy dataframe z konkretnymi kolumnami dla poszczególnych dni tygonia, województwa, firmy i rodzaju paliwa

#df2.to_csv(r'test.csv', decimal=',', sep=';')#potecjalny zapis pliku pozwaljący na pełny podgląd danych

X = np.array((df2.drop(['Prize'], axis=1)))#usunięcię z df2 kolumny z cenami, i przyisananie df2 do zmniennej "X"
y = np.array((df2['Prize']))
x_train, x_test, y_train, y_test = sklearn.model_selection.train_test_split(X, y, test_size=0.25)

def Save_Model ():
    #pętla wybierająca i zapisująca z 50 modeli, jeden z największą skutecznością.
    #Aby sprawdzić skuteczność, proszę usunąć plik 'FuelModel.pickle' i odkomentować wywołanie funkcji 'Save_Model()'"
    best_acc_score = 0 #pętla wybierająca i zapsijąca z z 50 modeli, jednen z największą skutecznością
    for acc_p in range(50):
        x_train, x_test, y_train, y_test = sklearn.model_selection.train_test_split(X, y, test_size=0.25)

        linear = linear_model.LinearRegression() #przypisanie do zmninnej 'linear' do funkcji regresjii liniowej

        linear.fit(x_train, y_train)
        acc = linear.score(x_test, y_test)
        print(acc)

        if acc > best_acc_score: #sprawdza i zapisuje najlepsy wynik z 50
            best_acc_score = acc
            with open('FuelModel.pickle', 'wb') as f:
                pickle.dump(linear, f)
Save_Model()
def Predict_and_visualise():
    linear = pickle.load(open('FuelModel.pickle', 'rb'))#otwiera i przypisuje model do zminnej 'linear'
    pre = linear.predict(x_test)#wykonuje predykcje cen
    acc = linear.score(x_test, y_test)
    for x in range(len(pre)): print(x_test[x], y_test[x],  pre[x])# zwaraca dane wejściowe(lista), cene adykwatną i predykcję tej ceny według modelu

    #wizualizacja zbieżności ceny przewidzianej i prawdziwej
    TruePrice = np.array([y_test[Tp] for Tp in range(len(pre))])
    PredictedPrice = np.array([pre[Pp] for Pp in range(len(pre))])

    style.use('ggplot')
    pyplot.scatter(PredictedPrice, TruePrice, 1)
    a, b = np.polyfit(PredictedPrice, TruePrice, 1)
    pyplot.plot(PredictedPrice, a * PredictedPrice + b)#tworzy linie regresjii
    pyplot.xlabel('Predicted Price')
    pyplot.ylabel("True Price")
    return pyplot.show()
Predict_and_visualise()