from bs4 import BeautifulSoup as BSoup
import requests
import pandas as pd
import datetime as dt

url_list = ['https://www.autocentrum.pl/stacje-paliw/pkn-orlen/',
            'https://www.autocentrum.pl/stacje-paliw/shell/',
            'https://www.autocentrum.pl/stacje-paliw/bp/',
            'https://www.autocentrum.pl/stacje-paliw/circle-k-statoil/']#lista witryn z których program scrappuje dane

def Scrapp_Petrol(url):
    r = requests.get(url)
    doc = BSoup(r.text, 'html.parser')
    # pobieranie danych ze strony
    company = doc.find(['h1'], class_='name')#szuka nazwy firmy z której pobiera dane
    date = doc.find_all(['td'], class_='date')#pobiera wszystkie daty z tabeli
    adress = doc.find_all(['td'], class_='address')# pobiera adresy poszczególnych rekordów
    prize = doc.find_all(['td'], class_='prize')#pobiera ceny poszczególnych rekordów

    def html_tag_cleaner(x): return [y.text for y in x] #czyści pobrane dane ze znaczników html

    fuels_type = [['95', '98', 'ON', 'ON+', 'LPG'], ['98', 'ON+', '100', '95', 'ON', 'LPG'], #lista możliwych konfiguracji paliw na poszczególnch stronach
                  ['95', '95+', '98', 'ON', 'ON+', 'LPG'], ['LPG', '95', 'ON', '98', 'ON+']]

    def fuel_list(x):#tworzy listę z rodzajem paliwa, powtarza rekord po 5 razy(tyle rekordów danego rodzaju paliwa znajduje się na każdej stronie)
        f = ''
        fuel = []
        for rodzaj in x:
            for i in range(0, 5):
                fuel.append(rodzaj)
        return fuel

    def current_date():#pobiera i normalizuję dzisiejszą datę
        today = dt.datetime.now()
        day = today.strftime('%d')
        month = today.strftime('%m')
        year = today.strftime('%Y')
        return f'{day}.{month}.{year}'

    # optymalizacja danych adresowych, dzieli listę z adresem w formie[adres, miasto i województwo] na dwie listy zawierające l1 = [adres i miasto]  oraz l2 = [województwo]
    clean_adress = html_tag_cleaner(adress)#wywołanie funkcji pozwala na uzskanie danych bez znaczników
    adress_city_list_cut = []
    province_list = []  # do df
    adress_city_list = []  # do df

    for x in clean_adress:
        ll = x.split()
        province_list.append(ll[-1])
        adress_city_list_cut.append(ll[:-2])
    for x in adress_city_list_cut:
        string = ''
        for y in x:
            string = string + ' ' + y
        adress_city_list.append(string)

    clean_prize = [cena[:-3] for cena in html_tag_cleaner(prize)]# tworzy listę zawierającą cenę bez znaczników html

    # przygowowanie danych do dataframe
    data = [] #dodanie wszystkich danych do listy pozwoli przy użyciu funkcji .transpose() konwersje na DataFrame
    data.append(html_tag_cleaner(date))
    # Na podstawie długości listy z datami decyduje sie jak wiele razy powtórzyć nazwę firmy w liście, jest to spowodowane różną ilością rekordów bo stacja shell ma 6  rodzajów paliw czyli łącznie 30 rekordów, resta tylko po 5 rodzajów paliw z sumą rekordów 25
    data.append(html_tag_cleaner(company) * 25 if len(date) == 25 else html_tag_cleaner(company) * 30)
    data.append(adress_city_list)
    data.append(province_list)
    #na postawie zawartości listy z rodzajem firmy decyduje, jaki rodzaj paliw z koknkretnej firmy przypisać. Spowodowane jest to różnym ułożeniem rodzaju paliw na poszczególnych stronach
    data.append(fuel_list(fuels_type[0]) if html_tag_cleaner(company) == ['PKN ORLEN'] else fuel_list(
        fuels_type[1]) if html_tag_cleaner(company) == ['Shell'] else fuel_list(fuels_type[2]) if html_tag_cleaner(
        company) == ['BP'] else fuel_list(fuels_type[3]))
    data.append(clean_prize)

    df0 = pd.DataFrame(data).transpose()#transpozycja listy w DataFame
    df0.columns = ['Date', 'Company', 'Adress', 'Province', 'Fuel', 'Prize']#Deklaracja nazwa kolumn
    #Jest mi wiadome że powinno się pisać 'Price', niestety naprawa tego błędu wymagałaby szeregu zmian w kodzie dlatego pozwoliłem sobie go pominąć

    df1 = df0[df0['Date'] == current_date()]#tworzy nowy dataframe bez rekordów z dni poprzednich(nie zawsze dane na stronie są uzupełniane na bierząco)
    df1.to_csv(r'PetrolData.csv', index=False, sep=';', mode='a', header=False)#nadpisaie pliku
    return print(df1)

for url in url_list: Scrapp_Petrol(url) #Wywołuje funkcje scrappowania i dla adresów url zawarych w liście adresów



