import tkinter
from tkinter import filedialog, IntVar, Checkbutton, Canvas, PhotoImage, Scale
import PIL
from PIL import ImageTk, Image
import multiprocessing


class OpenPage(tkinter.Frame):
    """
    Ramka z strony poczatkowej,
    otworzenie pliku z obrazem, zaladowanie obrazu do modelu,
    przejscie do kolejnej ramki
    """
    def open_btn(self):
        """
        Otwiera okno dialogowe z mozliwoscia wybrania pliku, nastepnie wysyla zadanie do kontrolera, o otworzenie wybranego pliku
        """
        if self.controller.open_image(filedialog.askopenfilename(initialdir = "/",title = "Select file", filetypes = (("png files","*.png"), ("jpg files","*.jpg")))):
            self.controller.show_frame("LibraryPage")

    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent)
        self.controller = controller

        # Przycisk do otworzenia pliku
        open_file_button = tkinter.Button(self, text = "Open", width = 12, height = 4, command = self.open_btn).pack()
        
        # Wyswietlenie przycisku w oknie
        #open_file_button.pack(pady = 15)


class LibraryPage(tkinter.Frame):

    def slider(self, event):
        """
        Na zmiane wartosci paska wyboru ilosci watkow
        sprawdza, czy ustawiona wartosc jest rowna ilosci rdzeni w procesorze,
        jesli tak wyswietla w oknie napis "Optimal"
        """
        if int(event) is self.threads_in_system:
            self.optimal_label.grid(row = 4, column = 1)
        else:
            self.optimal_label.grid_remove()

    def next_btn(self):
        """
        Tworzy obiekt z procesami w ilosci ustawionej przez uzytkownika,
        przekazuje ktora biblioteke wybral uzytkownik do nastepnego okna,
        przechodzi do nastepnego okna.
        """
        self.controller.set_library(self.library_var.get())
        self.controller.set_threads(self.threads.get())
        self.controller.show_frame("ImagePage")


    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent)
        self.controller = controller

        # Ilosc rdzeni w procesorze
        self.threads_in_system = multiprocessing.cpu_count()

        # Etykiety
        library_label = tkinter.Label(self, text = "Choose library", font = self.controller.title_font)
        threads_label = tkinter.Label(self, text = "Threads:", font = self.controller.title_font)
        self.optimal_label = tkinter.Label(self, text = "optimal", font = self.controller.title_font)
        
        # Przyciski
        # Powrot do poprzedniego okna
        back_button = tkinter.Button(self, text = "Back", width = 12, height = 4, command = lambda: self.controller.show_frame("OpenPage"))
        next_button = tkinter.Button(self, text = "Next", width = 12, height = 4, command = self.next_btn)

        # Pola wyboru biblioteki
        self.library_var = IntVar()
        self.library_var.set(0)
        python_library_checkbox = Checkbutton(self, text = "Python",    width = 12, variable = self.library_var, onvalue = 0, offvalue = 0)
        cpp_library_checkbox    = Checkbutton(self, text = "CPP",       width = 12, variable = self.library_var, onvalue = 1, offvalue = 1)
        asm_library_checkbox    = Checkbutton(self, text = "ASM",       width = 12, variable = self.library_var, onvalue = 2, offvalue = 2)
        
        # Pasek wyboru ilosci pracujacych procesow
        self.threads = Scale(self, from_= 0, to = 64, orient = "horizontal", command = self.slider)
        self.threads.set(self.threads_in_system)

        # Ustawienie wszystkiego w oknie
        library_label.grid          (row = 0, columnspan = 3)
        python_library_checkbox.grid(row = 1, column = 0)
        cpp_library_checkbox.grid   (row = 1, column = 1)
        asm_library_checkbox.grid   (row = 1, column = 2)
        threads_label.grid          (row = 2, columnspan = 3)
        self.threads.grid           (row = 3, columnspan = 3)
        back_button.grid            (row = 4, column = 0)
        self.optimal_label.grid     (row = 4, column = 1)
        next_button.grid            (row = 4, column = 2)


class ImagePage(tkinter.Frame):

    window = None

    def apply_btn(self):
        if self.window is not None:
            self.window.destroy()

        self.window = tkinter.Toplevel(self)

        self.time = self.controller.calculate(self.contrast.get())
        if self.time > 1:
            self.time_label.configure(text = "Time: " + str(round(self.time, 4)) + "s")
        else:
            self.time_label.configure(text = "Time: " + str(round(self.time * 1000, 4)) + "ms")
        
        # skalowanie obrazu do rozmiarow ekranu, jesli nie miesci sie na monitorze
        if self.controller.get_edited_image().size <= (self.controller.winfo_screenwidth(), self.controller.winfo_screenheight()):
            self.photoImage = ImageTk.PhotoImage(self.controller.get_edited_image())
        else:
            # operowanie na kopii obrazu, aby w przypadku zapisywania, zapisac obraz w pelnej rozdzielczosci
            self.image = self.controller.get_edited_image().copy()
            baseheight = self.controller.winfo_screenheight()
            hpercent = (baseheight / float(self.image.size[1]))
            wsize = int((float(self.image.size[0]) * float(hpercent)))
            self.image = self.image.resize((wsize, baseheight), PIL.Image.ANTIALIAS)
            self.photoImage = ImageTk.PhotoImage(self.image)

        # wyswietlenie obrazu w nowym oknie
        self.panel = tkinter.Label(self.window, image = self.photoImage)
        self.panel.pack()

    def back_btn(self):
        """
        Jesli okno z obrazem jest otworzone - zamyka je
        wraca do poprzedniego okna
        """
        if self.window is not None:
            self.window.destroy()
        self.controller.show_frame("LibraryPage")

    def save_btn(self):
        # Wyswietla okno dialogowe i wywoluje w modelu metode do zapisania obrazu w pliku o podanej sciezce
        self.controller.save_image(filedialog.asksaveasfilename())

    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent)
        self.controller = controller
        
        # Etykiety
        contrast_label = tkinter.Label(self, text = "Contrast modifier:", font = self.controller.title_font)
        self.time_label = tkinter.Label(self, text = "Time: ", font = self.controller.title_font)

        # Przyciski
        back_button = tkinter.Button(self, text = "Back", width = 12, height = 4, command = self.back_btn)
        apply_button = tkinter.Button(self, text = "Apply", width = 12, height = 4, command = self.apply_btn)
        save_button = tkinter.Button(self, text = "Save", width = 12, height = 4, command = self.save_btn)
        
        # Pasek z wyborem parametru alpha
        self.contrast = Scale(self, from_= 0.5, to = 5.0, resolution = 0.05, orient = "horizontal")
        self.contrast.set(1.0)

        # Wyswietlenie wszystkiego w oknie
        contrast_label.grid (row = 0, columnspan = 3)
        self.contrast.grid  (row = 1, column = 1)
        self.time_label.grid(row = 2, columnspan = 3)
        back_button.grid    (row = 3, column = 0, padx = 10)
        apply_button.grid   (row = 3, column = 1)
        save_button.grid    (row = 3, column = 2, padx = 10)


