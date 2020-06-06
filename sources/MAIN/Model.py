import multiprocessing
from PIL import Image
import time
from functools import partial
import ctypes

# Biblioteka Python [tworzona w projekcie PyLib skryptem PyLibSetup.py - tam tez jest okreslona sciezka, gdzie ta biblioteka ma trafic]
import PyLib

# Biblioteka CPP
CppLib = ctypes.cdll.LoadLibrary('../x64/Release/CppLib.dll')
# Ustawienie typów przyjmowanych parametrów przez funkcję
CppLib.create_LUT_array.argtypes = [ctypes.c_float]
CppLib.edit_data.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_int), ctypes.c_int]
# oraz typów zwracanych
CppLib.create_LUT_array.restype = ctypes.POINTER(ctypes.c_ubyte)
CppLib.edit_data.restype = ctypes.POINTER(ctypes.c_char)
# funkcja do przekazywania parametrow do biblioteki cpp w przypadku wielowatkowosci
def execute_cpp_function_with_multiprocessing(data, LUT_array, data_fragment_size):
    return CppLib.edit_data(data, (ctypes.c_int * 256)(*LUT_array), data_fragment_size)[0 : data_fragment_size]

# Biblioteka ASM
AsmLib = ctypes.cdll.LoadLibrary('../x64/Release/AsmLib.dll')

# Ustawienie typów przyjmowanych parametrów przez funkcję
AsmLib.create_LUT_array.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]
AsmLib.edit_data.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_char), ctypes.c_int]
# oraz typów zwracanych
AsmLib.create_LUT_array.restype = ctypes.POINTER(ctypes.c_char)
AsmLib.edit_data.restype = ctypes.POINTER(ctypes.c_char)
# funkcja do przekazywania parametrow do biblioteki cpp w przypadku wielowatkowosci
def execute_asm_function_with_multiprocessing(data, LUT_array, data_fragment_size):
    return AsmLib.edit_data(data, (ctypes.c_char * 256)(*LUT_array), data_fragment_size)[0 : data_fragment_size]


class Model(object):
    """
    Klasa modelu
    przechowuje dane o obrazach, procesach oraz tablice kontrastu [LUT]
    wykonuje modyfikacje obrazow z wykorzystaniem procesow lub na glownym watku
    """

#---IMAGES---------------------------------------
    def get_image(self):
        """
        Zwraca __image
        """
        return self.__image

    def set_image(self, image):
        """
        Ustawia __image

        @param image - obraz do ustawienia
        """
        self.__image = image

    def get_edited_image(self):
        """
        Zwraca __edited_image
        """
        return self.__edited_image

    def set_image(self, edited_image):
        """
        Ustawia edited_image

        @param edited_image - obraz do ustawienia
        """
        self.__edited_image = edited_image

    def open_image(self, path):
        """
        Otwiera obraz, sprawdza czy posiada on kanal alfa
        jesli nie - dodaje go.
        Otworzony obraz wpisywany jest do zmiennej __image
        oraz jego kopia do __edited_image

        @param path - sciezka do obrazu
        @return True - jesli udalo sie otworzyc obraz
        @return False - jesli nie udalo sie otworzyc obrazu
        """
        try:
            self.__image = Image.open(path)
            if self.__image.mode is 'RGB':
                self.__image.putalpha(255)
            self.__edited_image = self.__image.copy()
            return True
        except:
            print('Error while opening an image [%s]' %(path))
            return False

    def save_image(self, path):
        """
        Zapisuje obraz ze zmiennej __edited_image
        Do zmiennej __image przypisuje kopie __edited_image

        @param path - sciezka do zapisania pliku obrazu
        """
        try:
            self.get_edited_image().save(path)
            self.set_image(self.get_edited_image().copy())
        except:
            print('Error while saving an image')

    def image_get_data(self):
        """
        Z obrazu __image pobiera dane w formacie ciagu bajtow
        sa to wartosci poszczegolnych kanalow wszystkich pikseli
        RGBA RGBA RGBA...
        """
        try:
            return self.__image.tobytes()
        except:
            print('Error while getting byte data from image')
            return None

    def image_put_data(self, data):
        """
        Do obrazu __edited_image wprowadza dane w formacie ciagu bajtow
        sa to wartosci poszczeglonych kanalow wszystkich pikseli
        RGBA RGBA RGBA...
        @param data - ciag bajtow z danymi obrazu
        """
        try:
            self.__edited_image.frombytes(data)
        except:
            print('Error while putting byte data to image')

#---LUA-ARRAY------------------------------------
    def get_LUT_array(self):
        """
        Zwraca __LUT_array - tablica kontrastu
        """
        return self.__LUT_array

    def set_LUT_array(self, LUT_array):
        """
        Ustawia __LUT_array

        @param LUT_array - tablica kontrastu
        """
        self.__LUT_array = LUT_array

#---MULTIPROCESSING------------------------------
    def get_pool(self):
        """
        Zwraca __pool
        """
        return self.__pool

    def set_pool(self, pool):
        """
        Ustawia __pool

        @param pool - obiekt odpowiedzialny za wykonywanie operacji wieloprocesowo [wielowatkowo]
        """
        self.__pool = pool

    def create_pool(self, threads):
        """
        Tworzy obiekt odpowiedzialny za wykonywanie operacji wieloprocesowo [wielowatkowo]
        Ustawia ilosc procesow, ktore moga pracowac jednoczesnie

        @param threads - ile procesow moze pracowac jednoczesnie
        """
        if self.__pool:
            self.close_pool()
        if threads:
            self.__pool = multiprocessing.Pool(threads)

    def close_pool(self):
        """
        Konczy prace wieloprocesowa
        """
        if self.__pool:
            self.__pool.close()
            self.__pool.join()

    def calculate(self, alpha, lib, threading):
        """
        Pobiera dane z obrazu, modyfikuje je korzystajc z podanej biblioteki,
        zmodyfikowane dane wprowadza do drugiego obrazu.
        Mierzy i zwraca czas wykonania operacji.
        """
        # Pobierz dane z obrazy
        data = self.image_get_data()
        # Pobierz dlugosc dancyh
        data_size = len(data)
        # stworz pusta liste na zmodyfikowane dane
        new_data = b''
        # rozpocznil liczenie czasu
        start = time.time()
        
        #Glowny watek
        if not threading:
            #Python
            if lib is 0:  
                # Tworzenie tablicy LUT
                self.set_LUT_array(PyLib.create_LUT_array(alpha)[0:256])
                # edycja danych przez biblioteke
                new_data = PyLib.edit_data(data, self.get_LUT_array(), data_size)[0 : data_size]
            #Cpp
            elif lib is 1:
                # Tworzenie tablicy LUT
                self.set_LUT_array(CppLib.create_LUT_array(alpha)[0:256])
                # edycja danych przez biblioteke
                new_data = CppLib.edit_data(data, (ctypes.c_int * 256)(*self.get_LUT_array()), data_size)[0 : data_size]
            #Asm
            elif lib is 2:
                # Tworzenie tablicy LUT
                # przekazanie tablicy z wartosciami [0.0, ..., 255.0] oraz tablicy [alpha, alpha, alpha, alpha] dla ulatwienia wykonania operacji wektorowych w rejestrach xmm
                self.set_LUT_array(AsmLib.create_LUT_array((ctypes.c_float * 256)(*[float(i) for i in range(256)]), (ctypes.c_float * 4)(*[alpha, alpha, alpha, alpha]))[0:256])
                # edycja danych przez biblioteke
                new_data = AsmLib.edit_data(data, (ctypes.c_char * 256)(*self.get_LUT_array()), data_size)[0 : data_size]
        #wieloprocesowosc [wielowatkowosc]
        else:
            # Jak duzo danych przekazac na raz do pracujacego procesu
            # liczba zalezy od rozmiaru obrazu, uniemozliwia to sytuacje, w ktorej probujemy dostac sie do pamieci poza lista danych. 
            if data_size % 512:
                if data_size % 256:
                    if data_size % 128:
                        if data_size % 64:
                            if data_size % 32:
                                if data_size % 16:
                                    if data_size % 8:
                                        data_fragment_size = 4
                                    data_fragment_size = 8
                                data_fragment_size = 16
                            data_fragment_size = 32
                        data_fragment_size = 64
                    data_fragment_size = 128
                data_fragment_size = 256
            data_fragment_size = 512

            #Python
            if lib is 0:
                # Tworzenie tablicy LUT
                self.set_LUT_array(PyLib.create_LUT_array(alpha))
                # proces wykonuje funkcje z biblioteki na fragmencie danych o rozmiarze data_fragment_size
                # dane wiec sa dzielone na takie wlasnie fragmenty wykorzystujac obiekt generatora [polecenie iterator]
                # iteratorem jest tutaj petla for z wartosciami od 0 do data_size ze zmiana o data_fragment size
                # wynik dzialania wszystkich procesow na wszystkich fragmentach danych zapisywany jest w obiekcie __pool
                # w dokladnie tej samej kolejnosci, w jakiej sa zapisane dane obrazu w zmiennej data
                # wynik ten jest przekazywany do zmiennej arr jako tablica 2d bajtow
                arr = [self.get_pool().map(
                    partial(PyLib.edit_data, LUT_array = self.get_LUT_array(), data_fragment_size = data_fragment_size),
                    [data[i : i + data_fragment_size]
                    for i in range(0, data_size, data_fragment_size)])][0]
            #Cpp
            elif lib is 1:
                # Tworzenie tablicy LUT
                self.set_LUT_array(CppLib.create_LUT_array(alpha)[0:256])         
                # proces wykonuje funkcje z biblioteki na fragmencie danych o rozmiarze data_fragment_size
                # dane wiec sa dzielone na takie wlasnie fragmenty wykorzystujac obiekt generatora [polecenie iterator]
                # iteratorem jest tutaj petla for z wartosciami od 0 do data_size ze zmiana o data_fragment size
                # wynik dzialania wszystkich procesow na wszystkich fragmentach danych zapisywany jest w obiekcie __pool
                # w dokladnie tej samej kolejnosci, w jakiej sa zapisane dane obrazu w zmiennej data
                # wynik ten jest przekazywany do zmiennej arr jako tablica 2d bajtow
                arr = [self.get_pool().map(
                    partial(execute_cpp_function_with_multiprocessing, LUT_array = self.get_LUT_array(), data_fragment_size = data_fragment_size),
                    [data[i : i + data_fragment_size]
                    for i in range(0, data_size, data_fragment_size)])][0]
            #Asm
            elif lib is 2:
                # Tworzenie tablicy LUT
                self.set_LUT_array(AsmLib.create_LUT_array(((ctypes.c_float * 256)(*([float(i) for i in range(256)]))), ((ctypes.c_float * 4)(*([alpha] * 4))))[0:256])
                # proces wykonuje funkcje z biblioteki na fragmencie danych o rozmiarze data_fragment_size
                # dane wiec sa dzielone na takie wlasnie fragmenty wykorzystujac obiekt generatora [polecenie iterator]
                # iteratorem jest tutaj petla for z wartosciami od 0 do data_size ze zmiana o data_fragment size
                # wynik dzialania wszystkich procesow na wszystkich fragmentach danych zapisywany jest w obiekcie __pool
                # w dokladnie tej samej kolejnosci, w jakiej sa zapisane dane obrazu w zmiennej data
                # wynik ten jest przekazywany do zmiennej arr jako tablica 2d bajtow
                arr = [self.get_pool().map(
                    partial(execute_asm_function_with_multiprocessing, LUT_array = self.get_LUT_array(), data_fragment_size = data_fragment_size),
                    [data[i : i + data_fragment_size]
                    for i in range(0, data_size, data_fragment_size)])][0]

            # dopisanie do new_data danych z tablicy arr
            new_data = new_data.join([arr[i][0 : data_fragment_size] for i in range(len(arr))])

        # wstaw nowe dane do obrazu
        self.image_put_data(new_data)

        # skoncz liczenie czasu
        end = time.time()

        return end - start


#---OTHER----------------------------------------
    # konstruktor
    def __init__(self):
        # Przygotowanie zmiennych
        self.__image = None
        self.__edited_image = None
        self.__LUT_array = bytes([i for i in range(256)])
        self.__pool = None
    
    # destruktor
    def __del__(self):
        self.close_pool()