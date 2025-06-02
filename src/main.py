import tkinter as tk
from fenetre_generation import FenetreGeneration
from fenetre_horaire import FenetreHoraire
from generateur import Generateur
from lecteur import charger_cours_depuis_fichier

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Générateur d'horaires")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.fenetre_active = None
        self.changer_fenetre("generation")

    def changer_fenetre(self, nom, nb_cours_optionnels=-1):
        if self.fenetre_active is not None:
            self.fenetre_active.destroy()
 
        if nom == "generation":
            self.fenetre_active = FenetreScrollable(self, FenetreGeneration, self.changer_fenetre)
            self.geometry("800x1000")

        elif nom == "horaire":
            cours_obligatoires, cours_optionnels = charger_cours_depuis_fichier()
            gen = Generateur(cours_obligatoires, cours_optionnels, nb_cours_optionnels)
            gen.creer_horaires()
            horaires = gen.horaires

            self.fenetre_active = FenetreScrollable(self, FenetreHoraire, self.changer_fenetre, horaires)
            self.geometry("1400x1200")

        else:
            raise ValueError(f"Fenêtre inconnue : {nom}")

        self.fenetre_active.grid(row=0, column=0, sticky="nsew")

class FenetreScrollable(tk.Frame):
    def __init__(self, parent, classe_contenu, *args, **kwargs):
        super().__init__(parent)

        canvas = tk.Canvas(self)
        scrollbarV = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbarV.set)
        scrollbarH = tk.Scrollbar(self, orient="horizontal", command=canvas.xview)
        canvas.configure(xscrollcommand=scrollbarH.set)

        canvas.grid(row=1, column=0, sticky="nsew")
        scrollbarV.grid(row=1, column=1, sticky="ns")
        scrollbarH.grid(row=0, column=0, sticky="ew")

        cadre_contenu = tk.Frame(canvas)
        window_id = canvas.create_window((0, 0), window=cadre_contenu, anchor="nw")
        
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(window_id, width=e.width))
        cadre_contenu.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        self.contenu = classe_contenu(cadre_contenu, *args, **kwargs)
        self.contenu.grid(row=0, column=0, sticky="nsew")

        cadre_contenu.grid_rowconfigure(0, weight=1)
        cadre_contenu.grid_columnconfigure(0, weight=1)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

if __name__ == "__main__":
    app = App()
    app.mainloop()