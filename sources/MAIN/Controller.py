import tkinter
from tkinter import font
from tkinter import *

import Model

from View import *


class Controller(tkinter.Tk):
    """
    Klasa kontrolera
    komunikacja pomiedzy modelem i widokiem
    """
    # zmienne do przekazania pomiedzy widokiem i modelem
    __library = 0
    __threads = 0

    def set_library(self, library):
        """
        Ustawia __library

        @param library - numer biblioteki do wykonania
        """
        self.__library = library
    
    def set_threads(self, threads):
        """
        Ustawia __threading
        Wywoluje w modelu metode create_pool()
        
        @param threads - ile procesow moze pracowac jednoczesnie
        """
        self.__threads = threads
        self.__model.create_pool(threads)

    def get_model(self):
        """
        Zwraca __model
        """
        return self.__model

    def set_model(self, model):
        """
        Ustawia __model

        @param model - model
        """
        self.__model = model

    def get_image(self):
        """
        Pobiera __image z modelu i zwraca
        """
        return self.__model.get_image()

    def get_edited_image(self):
        """
        Pobiera __edited_image z modelu i zwraca
        """
        return self.__model.get_edited_image()

    def open_image(self, path):
        """
        Wywoluje w modelu metode open_image()

        @param path - sciezka do pliku z obrazem
        @return True - jesli udalo sie otworzyc obraz
        @return False - jesli nie udalo sie otworzyc obrazu
        """
        return self.__model.open_image(path)

    def save_image(self, path):
        """
        Wywoluje w modelu metode save_image()

        @param path - sciezka gdzie ma byc zapisany plik z obrazem
        """
        self.__model.save_image(path)

    def calculate(self, alpha):
        """
        Wywoluje w modelu metode calculate()

        @param alpha - wspolczynnik kontrastu,
        @param lib - ktora biblioteka ma zostac wykonana [Py, Cpp, Asm]
        @param threading - czy biblioteka ma byc wykonana na glownym watku, czy wielowatkowo
        """
        return self.__model.calculate(alpha, self.__library, self.__threads)

    def show_frame(self, page_name):
        """
        Pokazuje ramke o podanej nazwie strony

        @param page_name - nazwa strony, ktora ma zostac wyswietlona
        """
        frame = self.frames[page_name]
        frame.tkraise()

    def __init__(self):
        tkinter.Tk.__init__(self)
        self.title_font = font.Font(family = 'Helvetica', size = 18, weight = "bold", slant = "italic")
        self.__model = Model.Model()

        # Tworzenie i ustawienie kontenera na ramki stron
        container = tkinter.Frame(self)
        container.pack(side = "top", fill = "both")
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)
        self.frames = {}
        
        # Tworzenie ramek i dodawanie ich do kontenera
        # ramka na szczycie, jest widoczna dla uzytkownika
        # [Ramki sa zdefiniowane w klasie View]
        for F in (OpenPage, LibraryPage, ImagePage):
            page_name = F.__name__
            frame = F(parent = container, controller = self)
            self.frames[page_name] = frame
            frame.grid(row = 3, column = 3, sticky = "nsew")

        # ustaw na szczyt ramke o nazwie OpenPage
        self.show_frame("OpenPage")