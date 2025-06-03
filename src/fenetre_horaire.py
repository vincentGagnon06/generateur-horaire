"""
Auteur : Vincent Gagnon
Date : Juin 2025
Ce fichier permet de gérer l'interface de création des horaires.
"""

import tkinter as tk
from tkinter import ttk
from generateur import GroupeHoraire

JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
HEURES_DEMI = [8 + i * 0.5 for i in range((21 - 8) * 2 - 1)] #8 à 20
PALETTE_COULEURS = [
    "#FFB3BA", "#FFDFBA", "#FFFFBA", "#BAFFC9", "#BAE1FF",
    "#D7BAFF", "#FFC0CB", "#C0C0FF", "#B0E0E6", "#E6E6FA",
    "#98FB98", "#FFDAB9", "#E0FFFF"
]

class FenetreHoraire(tk.Frame):
    def __init__(self, master, changer_fenetre, horaires):
        super().__init__(master)
        self.changer_fenetre = changer_fenetre
        self.horaires: list[tuple[int, list[GroupeHoraire]]] = [(i+1, h) for i, h in enumerate(horaires)]
        self.horaire_selectionne: int = 0
        self.couleurs_cours: dict[str, str] = {}

        self.setup_ui()

    def setup_ui(self):
        def centrer_tableau(event):
            canvas_width = event.width
            frame_width = self.tableau_frame.winfo_reqwidth()
            x = max((canvas_width - frame_width) // 2, 0)
            self.tableau_canvas.coords(self.tableau_window, x, 0)

        # Centrage principal
        self.container = ttk.Frame(self)
        self.container.pack(expand=True)

        # Cadre des rectangles en haut
        self.rectangles_frame = ttk.Frame(self.container)
        self.rectangles_frame.pack(pady=15)

        self.afficher_rectangles()

        # Tableau dans un Canvas pour éventuel débordement
        self.tableau_canvas = tk.Canvas(self.container, width=1400, height=800)
        self.tableau_canvas.pack(fill="both", expand=True, padx=20, pady=15)
        self.tableau_frame = tk.Frame(self.tableau_canvas, bg="white")
        self.tableau_window = self.tableau_canvas.create_window((0, 0), window=self.tableau_frame, anchor="n")
        self.tableau_canvas.bind("<Configure>", centrer_tableau)
        self.tableau_frame.bind(
            "<Configure>",
            lambda e: self.tableau_canvas.configure(scrollregion=self.tableau_canvas.bbox("all"))
        )

        self.afficher_tableau()

        # Style pour les boutons
        style = ttk.Style()
        style.configure("Custom.TButton", font=("Arial", 12, "bold"), padding=10)
        
        # Boutons sous le tableau, avec fond
        btns_frame = tk.Frame(
            self.container,
            highlightbackground="white",
            highlightthickness=2,
            bd=1,
            relief="solid"
        )
        btns_frame.pack(pady=15, fill="x", padx=20)

        # Sous-frame centré pour les boutons
        boutons_centres = tk.Frame(btns_frame)
        boutons_centres.pack()

        btn_supprimer = ttk.Button(
            boutons_centres,
            text="Supprimer l’horaire actuel",
            command=self.supprimer_horaire_selectionne,
            style="Custom.TButton"
        )
        btn_supprimer.pack(side="left", padx=15, pady=10)

        btn_modifier = ttk.Button(
            boutons_centres,
            text="Modifier les cours",
            command=lambda: self.changer_fenetre("generation"),
            style="Custom.TButton"
        )
        btn_modifier.pack(side="left", padx=15, pady=10)

    def afficher_rectangles(self):
        for widget in self.rectangles_frame.winfo_children():
            widget.destroy()

        if not self.horaires:
            label = tk.Label(
                self.rectangles_frame,
                text="Aucun horaire disponible",
                font=("Arial", 14, "italic"),
                fg="gray"
            )
            label.pack()
            return

        for i, (id_horaire, _) in enumerate(self.horaires):
            est_selectionne = (i == self.horaire_selectionne)

            frame = tk.Frame(
                self.rectangles_frame,
                bd=3 if est_selectionne else 1,
                relief="solid",
                padx=12,
                pady=6,
                bg="#cce5ff" if est_selectionne else "#f0f0f0"
            )
            frame.pack(side="left", padx=10)

            label = tk.Label(
                frame,
                text=f"Horaire #{id_horaire}",
                bg=frame["bg"],
                fg="black",
                font=("Arial", 14, "bold" if est_selectionne else "normal")
            )
            label.pack()
            label.bind("<Button-1>", lambda e, index=i: self.selectionner_horaire(index))

    def supprimer_horaire_selectionne(self):
        if self.horaires:
            del self.horaires[self.horaire_selectionne]
            if self.horaire_selectionne >= len(self.horaires):
                self.horaire_selectionne = max(0, len(self.horaires) - 1)
            self.afficher_rectangles()
            self.afficher_tableau()

    def selectionner_horaire(self, index):
        self.horaire_selectionne = index
        self.afficher_rectangles()
        self.afficher_tableau()

    def couleur_pour_sigle(self, sigle):
        if sigle not in self.couleurs_cours:
            index = len(self.couleurs_cours) % len(PALETTE_COULEURS)
            self.couleurs_cours[sigle] = PALETTE_COULEURS[index]
        return self.couleurs_cours[sigle]
    
    def texte_contraste(self, bg_hex):
        r = int(bg_hex[1:3], 16)
        g = int(bg_hex[3:5], 16)
        b = int(bg_hex[5:7], 16)
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        return 'black' if luminance > 186 else 'white'

    def afficher_tableau(self):
        for widget in self.tableau_frame.winfo_children():
            widget.destroy()

        # En-têtes de jours
        for j, jour in enumerate([""] + JOURS):
            label = tk.Label(
                self.tableau_frame,
                text=jour,
                borderwidth=1,
                relief="solid",
                width=18,
                height=3,
                bg="white",
                fg="black",
                anchor="center"
            )
            label.grid(row=0, column=j, sticky="nsew")
            self.tableau_frame.grid_columnconfigure(j, weight=1)

        # En-têtes d’heures (une cellule couvre deux demi-heures)
        for i, heure in enumerate(range(8, 21)):
            label = tk.Label(
                self.tableau_frame,
                text=f"{heure}:00",
                borderwidth=1,
                relief="solid",
                height=3,
                bg="white",
                fg="black",
                anchor="center"
            )
            label.grid(row=2*i+1, column=0, rowspan=2, sticky="nsew")
            self.tableau_frame.grid_rowconfigure(2*i+1, weight=1)
            self.tableau_frame.grid_rowconfigure(2*i+2, weight=1)

        # Grille vide (1 cellule par heure)
        for i, heure in enumerate(range(8, 21)):
            for j in range(len(JOURS)):
                col = j + 1
                row = (heure - 8) * 2 + 1
                label = tk.Label(
                    self.tableau_frame,
                    text="",
                    bg="white",
                    borderwidth=0.5,
                    relief="solid",
                    height=2
                )
                label.grid(row=row, column=col, rowspan=2, sticky="nsew")

        if not self.horaires:
            return

        _, horaire = self.horaires[self.horaire_selectionne]
        for groupe in horaire:
            for jour, debut, fin in groupe.plages:
                if jour not in JOURS:
                    continue

                col = JOURS.index(jour) + 1
                row_debut = int((debut - 8) * 2) + 1  # Convertit en demi-heures
                row_fin = int((fin - 8) * 2) + 1
                rowspan = row_fin - row_debut

                texte = f"{groupe.cours.sigle} - {groupe.nom_groupe}"
                bg = self.couleur_pour_sigle(groupe.cours.sigle)
                fg = self.texte_contraste(bg)
                label = tk.Label(
                    self.tableau_frame,
                    text=texte,
                    bg=bg,
                    fg=fg,
                    borderwidth=1,
                    relief="solid",
                    wraplength=120,
                    justify="center"
                )
                label.grid(row=row_debut, column=col, rowspan=rowspan, sticky="nsew")

                for r in range(row_debut, row_debut + rowspan):
                    self.tableau_frame.grid_rowconfigure(r, weight=1)