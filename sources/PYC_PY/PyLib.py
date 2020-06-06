def create_LUT_array(alpha):
    """
	Funkcja tablicujaca wartosci pikseli w zaleznosci od parametru alpha.

	@param alpha - wspolczynnik kontrastu
	@return LUT_array - tablica [lista] LUT
    """

    # Przygotuj pusta tablice [liste] LUT
    LUT_array = []

    # wzor na wartosc i-tego elementu tablicy:
    # 0                         jesli (i - 128) * alpha + 128 <= 0
    # (i - 128) * alpha + 128   jesli (i - 128) * alpha + 128 jest w przedziale (0, 255)
    # 255                       jesli (i - 128) * alpha + 128 >= 255
    # indeks ostatniego elementu do ktorego powinna byc wpisana wartosc 0
    last_x00_id = int(-128 // alpha + 129)
    # indeks pierwszego elementu od ktorego powinna byc wpisana wartosc 255
    first_xff_id = int(128 // alpha + 128)

    # Rozszerzenie tablicy [listy] o wartosci wynikajace ze wzoru
    # zastosowanie obiektu generatora [polecenie iterator] do rozszerzania tablicy
    # wykonuje polecenie zadeklarowane na poczatku dla kazdej iteracji wynikajacej z wewnetrznej petli for
    [LUT_array.append(0) for _ in range(last_x00_id)]
    [LUT_array.append(int((channel - 128) * alpha + 128)) for channel in range(last_x00_id, first_xff_id)]
    [LUT_array.append(255) for _ in range(first_xff_id, 256)]

    return LUT_array

def edit_data(data, LUT_array, data_fragment_size):
    """
    Funkcja podmieniajaca wartosci w tablicy z danymi, wartosciami z tablicy LUT.
    jesli kanal R ma wartosc 17, to jego wartosc po zmienie kontrastu jest
    zapisana w tablicy LUT w elemencie o indeksie 17
    R = LUT[R]

	@param data - ciag danych do podmienienia
	@param LUT_array - tablica LUT
	@data_fragment_size - jak duzo danych ma zostac podmienionych
	@return new_data - ciag podmienionych danych
    """
    # Przygotowanie nowej listy z danymi po podmienieniu
    new_data = [None] * data_fragment_size

    for i in range(0, data_fragment_size, 4):
        # podstawienie wartosci kanalu R
        new_data[i + 0] = LUT_array[data[i + 0]]
        # podstawienie wartosci kanalu G
        new_data[i + 1] = LUT_array[data[i + 1]]
        # podstawienie wartosci kanalu B
        new_data[i + 2] = LUT_array[data[i + 2]]
        # kanal A pozostaje bez zmian
        new_data[i + 3] = data[i + 3]
    
    return bytes(new_data)