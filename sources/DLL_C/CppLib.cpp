#include <cstddef>
#define cDLL extern "C" __declspec(dllexport)

/**
	Funkcja tablicujaca wartosci pikseli w zaleznosci od parametru alpha.

	@param alpha - wspolczynnik kontrastu
	@return LUT_array - wskaznik na utworzona tablice LUT
*/
cDLL std::byte* create_LUT_array(float alpha) {
	// Przygotuj nowa tablice LUT
	std::byte* LUT_array = new std::byte[256]{ std::byte(0) };

	// wzor na wartosc i - tego elementu tablicy :
	// 0                         jesli(i - 128) * alpha + 128 <= 0
	// (i - 128) * alpha + 128   jesli (i - 128) * alpha + 128 jest w przedziale (0, 255)
	// 255                       jesli(i - 128) * alpha + 128 >= 255
	// indeks ostatniego elementu do ktorego powinna byc wpisana wartosc 0
	int last_x00_id = int(-128 / alpha) + 128;
	// indeks pierwszego elementu od ktorego powinna byc wpisana wartosc 255
	int first_xff_id = int(128 / alpha) + 128;

	// wpisanie odpowiednich wartosci do tablicy LUT
	for (int i = 0; i < 256; i++) {
		if (i < last_x00_id)		LUT_array[i] = std::byte(0);
		else if (i < first_xff_id)	LUT_array[i] = std::byte(int((i - 128) * alpha + 128));
		else						LUT_array[i] = std::byte(255);
	}

	return LUT_array;
}

/**
	Funkcja podmieniajaca wartosci w tablicy z danymi, wartosciami z tablicy LUT.
    jesli kanal R ma wartosc 17, to jego wartosc po zmienie kontrastu jest
    zapisana w tablicy LUT w elemencie o indeksie 17
    R = LUT[R]

	@param data - ciag danych do podmienienia
	@param LUT_array - tablica LUT
	@data_fragment_size - jak duzo danych ma zostac podmienionych
	@return data - ciag podmienionych danych
*/
cDLL std::byte* edit_data(std::byte* data, int* LUT_array, int data_fragment_size) {
	for (int i = 0; i <= data_fragment_size; i += 4) {
		// podstawienie wartosci do kanalu R
		data[i + 0] = std::byte(LUT_array[int(data[i + 0])]);
		// podstawienie wartosci do kanalu G
		data[i + 1] = std::byte(LUT_array[int(data[i + 1])]);
		// podstawienie wartosci do kanalu B
		data[i + 2] = std::byte(LUT_array[int(data[i + 2])]);
		// kanal A pozostaje bez zmian
	}

	return data;
}