"""
Auteur : Vincent Gagnon
Date : Juin 2025
Ce fichier contient les fonctions permettant d'afficher et de gérer l'interface d'ajouts de cours.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from generateur import Cours, GroupeHoraire
import lecteur

class FenetreGeneration(tk.Frame):
    def __init__(self, master, changer_fenetre):
        super().__init__(master)
        self.changer_fenetre = changer_fenetre

        self.cours_obligatoires = []
        self.cours_optionnels = []
        self.groupes_temp = []

        self.setup_ui()
        self.initialiser_cours()

    def setup_ui(self):
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.creer_section_ajout()
        self.creer_section_listes()
        self.creer_section_details()
        self.creer_boutons_generaux()
        self.creer_section_generation()

    def creer_section_ajout(self):
        frame = ttk.LabelFrame(self, text="Ajouter un cours")
        frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        frame.columnconfigure(1, weight=1)

        def label(row, text):
            ttk.Label(frame, text=text).grid(row=row, column=0, sticky="e")

        def entry(row):
            e = ttk.Entry(frame)
            e.grid(row=row, column=1, sticky="ew")
            return e

        label(0, "Sigle:")
        self.entry_sigle = entry(0)
        label(1, "Nom:")
        self.entry_nom = entry(1)

        self.var_obligatoire = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Obligatoire", variable=self.var_obligatoire).grid(row=2, column=0, columnspan=2)
        ttk.Separator(frame, orient="horizontal").grid(row=3, column=0, columnspan=2, sticky="ew", pady=5)

        label(4, "Nom du groupe:")
        self.entry_nom_groupe = entry(4)

        self.frame_plages = ttk.LabelFrame(frame, text="Plages horaires")
        self.frame_plages.grid(row=5, column=0, columnspan=2, sticky="ew", pady=5)
        self.frame_plages.columnconfigure((0, 1, 2), weight=1)

        for i, t in enumerate(["Jour", "Début", "Fin"]):
            ttk.Label(self.frame_plages, text=t).grid(row=0, column=i)

        self.lignes_plages = []
        ttk.Button(self.frame_plages, text="Ajouter une ligne", command=self.ajouter_ligne_plage).grid(row=999, column=0, columnspan=3, pady=3)
        ttk.Button(self.frame_plages, text="Retirer la dernière ligne", command=self.retirer_ligne_plage).grid(row=1000, column=0, columnspan=3, pady=3)

        ttk.Button(frame, text="Ajouter groupe au cours", command=self.ajouter_groupe).grid(row=6, column=0, columnspan=2, pady=2)
        ttk.Button(frame, text="Réinitialiser le groupe", command=self.reinitialiser_groupe).grid(row=7, column=0, columnspan=2, pady=(0, 5))

        self.label_groupes_temp = ttk.Label(frame, text="Groupes ajoutés : 0")
        self.label_groupes_temp.grid(row=8, column=0, columnspan=2)

        ttk.Separator(frame, orient="horizontal").grid(row=9, column=0, columnspan=2, sticky="ew", pady=(5, 5))

        ttk.Button(frame, text="Ajouter le cours", command=self.ajouter_cours).grid(row=10, column=0, columnspan=2, pady=5)
        ttk.Button(frame, text="Réinitialiser le cours", command=self.reinitialiser_cours).grid(row=11, column=0, columnspan=2, pady=(0, 10))

    def creer_section_listes(self):
        frame = ttk.LabelFrame(self, text="Cours ajoutés")
        frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        frame.columnconfigure((0, 1), weight=1)
        frame.rowconfigure(1, weight=1)

        ttk.Label(frame, text="Obligatoires").grid(row=0, column=0)
        self.liste_obligatoires = tk.Listbox(frame)
        self.liste_obligatoires.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.liste_obligatoires.bind("<<ListboxSelect>>", self.afficher_details_cours)

        ttk.Label(frame, text="Optionnels").grid(row=0, column=1)
        self.liste_optionnels = tk.Listbox(frame)
        self.liste_optionnels.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        self.liste_optionnels.bind("<<ListboxSelect>>", self.afficher_details_cours)

    def creer_section_details(self):
        frame = ttk.LabelFrame(self, text="Détails du cours")
        frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        self.details_label = ttk.Label(frame, text="Sélectionnez un cours pour voir ses détails.")
        self.details_label.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

    def creer_boutons_generaux(self):
        ttk.Button(self, text="Cacher détails", command=self.cacher_details).grid(row=3, column=0, pady=(0, 10))
        ttk.Button(self, text="Supprimer le cours", command=self.supprimer_cours).grid(row=4, column=0, pady=(0, 10))
        ttk.Separator(self, orient="horizontal").grid(row=5, column=0, sticky="ew", pady=(5, 5))

        ttk.Button(self, text="Sauvegarder", command=self.sauvegarder_cours).grid(row=6, column=0, pady=(0, 10))
        ttk.Button(self, text="Réinitialiser", command=self.reinitialiser_horaire).grid(row=7, column=0, pady=(0, 10))
    
    def creer_section_generation(self):
        frame = ttk.LabelFrame(self, text="Génération")
        frame.grid(row=8, column=0, sticky="ew", padx=10, pady=10)
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Nombre de cours optionnels à inclure:").grid(row=0, column=0, sticky="e")
        self.entry_nb_cours_option = ttk.Entry(frame)
        self.entry_nb_cours_option.grid(row=0, column=1, sticky="ew")
        self.entry_nb_cours_option.insert(0, "0")

        ttk.Button(frame, text="Générer les horaires", command=self.generer_horaires).grid(row=1, column=0, columnspan=2, pady=(0, 10))

    def generer_horaires(self):
        try:
            nb_cours_optionnels = int(self.entry_nb_cours_option.get().strip())
            if not 0 <= nb_cours_optionnels <= len(self.cours_optionnels):
                raise ValueError("Nombre hors limites")
            
            self.sauvegarder_cours(afficher_message=False)
            self.changer_fenetre("horaire", nb_cours_optionnels=nb_cours_optionnels)

        except ValueError:
            messagebox.showerror("Erreur", "Entrez un nombre de cours optionnels valide")
            return

    def afficher_details_cours(self, event):
        selection_obligatoire = self.liste_obligatoires.curselection()
        selection_optionnelle = self.liste_optionnels.curselection()

        if selection_obligatoire:
            index = selection_obligatoire[0]
            cours = self.cours_obligatoires[index]
        elif selection_optionnelle:
            index = selection_optionnelle[0]
            cours = self.cours_optionnels[index]
        else:
            return

        details_text = f"Sigle : {cours.sigle}\nNom : {cours.nom}\n"
        details_text += f"Obligatoire : {'Oui' if cours.obligatoire else 'Non'}\n\n"

        if cours.groupes:
            details_text += "Groupes :\n"
            for groupe in cours.groupes:
                details_text += f"  - {groupe.nom_groupe} :\n"
                for plage in groupe.plages:
                    heure_debut = str(int(plage[1]))
                    minute_debut_decimal = int(60 * (plage[1] - int(plage[1])))
                    minute_debut = str(minute_debut_decimal) if minute_debut_decimal >= 10 else "0" + str(minute_debut_decimal)

                    heure_fin = str(int(plage[2]))
                    minute_fin_decimal = int(60 * (plage[2] - int(plage[2])))
                    minute_fin = str(minute_fin_decimal) if minute_fin_decimal >= 10 else "0" + str(minute_fin_decimal)

                    details_text += f"    {plage[0]} : {heure_debut}h{minute_debut} - {heure_fin}h{minute_fin}\n"
        else:
            details_text += "Aucun groupe ajouté."

        self.details_label.config(text=details_text)

    def cacher_details(self):
        self.details_label.config(text="Sélectionnez un cours pour voir ses détails.")

        self.liste_obligatoires.selection_clear(0, tk.END)
        self.liste_optionnels.selection_clear(0, tk.END)

    def ajouter_ligne_plage(self):
        row = len(self.lignes_plages) + 1

        # Jour en liste déroulante
        jours = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
        jour = ttk.Combobox(self.frame_plages, values=jours, state="readonly", justify="center")

        # Heure début
        frame_debut = ttk.Frame(self.frame_plages)
        entry_heure_debut = ttk.Entry(frame_debut, width=2, justify="center")
        entry_minute_debut = ttk.Entry(frame_debut, width=2, justify="center")
        entry_minute_debut.insert(0, "00")

        entry_heure_debut.pack(side="left")
        ttk.Label(frame_debut, text="h").pack(side="left")
        entry_minute_debut.pack(side="left")

        # Heure fin
        frame_fin = ttk.Frame(self.frame_plages)
        entry_heure_fin = ttk.Entry(frame_fin, width=2, justify="center")
        entry_minute_fin = ttk.Entry(frame_fin, width=2, justify="center")
        entry_minute_fin.insert(0, "00")

        entry_heure_fin.pack(side="left")
        ttk.Label(frame_fin, text="h").pack(side="left")
        entry_minute_fin.pack(side="left")

        # Placement dans la grille
        jour.grid(row=row, column=0, sticky="ew", padx=2, pady=1)
        frame_debut.grid(row=row, column=1, padx=2, pady=1)
        frame_fin.grid(row=row, column=2, padx=2, pady=1)

        # Sauvegarde dans la liste des lignes
        self.lignes_plages.append((jour, frame_debut, frame_fin))

    def retirer_ligne_plage(self):
        for champ in self.lignes_plages[-1]:
            champ.destroy()
        self.lignes_plages.pop(-1)

    def reinitialiser_groupe(self, demander_confirmation=True):
        if demander_confirmation:
            confirmation = self.demander_confirmation("Êtes-vous certain de vouloir supprimer ce groupe? Cette action est irréversible.")
            if not confirmation:
                return
            
        self.entry_nom_groupe.delete(0, tk.END)
        for e in self.lignes_plages:
            for champ in e:
                champ.destroy()
        self.lignes_plages.clear()
        self.label_groupes_temp.config(text=f"Groupes ajoutés : {len(self.groupes_temp)}")

    def ajouter_groupe(self):
        nom = self.entry_nom_groupe.get().strip()
        if not nom:
            messagebox.showerror("Erreur", "Le nom du groupe est requis.")
            return
        
        if any(g.nom_groupe.lower() == nom.lower() for g in self.groupes_temp):
            messagebox.showerror("Erreur", f"Un groupe ayant le nom {nom} à déjà été ajouté.")
            return

        groupe = GroupeHoraire(nom)

        for jour_cb, frame_debut, frame_fin in self.lignes_plages:
            jour = jour_cb.get().strip().lower()

            enfants_debut = frame_debut.winfo_children()
            h_debut_e = enfants_debut[0]
            m_debut_e = enfants_debut[1]

            enfants_fin = frame_fin.winfo_children()
            h_fin_e = enfants_fin[0]
            m_fin_e = enfants_fin[1]

            if not jour:
                messagebox.showerror("Erreur", "Veuillez sélectionner un jour.")
                return

            try:
                h_debut = int(h_debut_e.get())
                m_debut = int(m_debut_e.get())
                h_fin = int(h_fin_e.get())
                m_fin = int(m_fin_e.get())
            except ValueError:
                messagebox.showerror("Erreur", "Les heures et minutes doivent être des nombres.")
                return

            if not (0 <= m_debut < 60 and 0 <= m_fin < 60):
                messagebox.showerror("Erreur", "Les minutes doivent être entre 0 et 59.")
                return

            debut = h_debut + m_debut / 60
            fin = h_fin + m_fin / 60

            if not 8 <= debut <= 20 or not 8 <= fin <= 20:
                messagebox.showerror("Erreur", "Les heures doivent être entre 8h00 et 20h00.")
                return

            if debut >= fin:
                messagebox.showerror("Erreur", "L'heure de début doit être inférieure à l'heure de fin.")
                return

            groupe.plages.append((jour, debut, fin))

        if not groupe.plages:
            messagebox.showerror("Erreur", "Aucune plage horaire définie pour ce groupe.")
            return

        self.groupes_temp.append(groupe)
        messagebox.showinfo("Ajouté", f"Groupe {nom} ajouté au cours.")

        self.reinitialiser_groupe(demander_confirmation=False)

    def reinitialiser_cours(self, demander_confirmation=True):
        if demander_confirmation:
            confirmation = self.demander_confirmation("Êtes-vous certain de vouloir supprimer tous les groupes de ce cours? Cette action est irréversible.")
            if not confirmation:
                return

        self.entry_sigle.delete(0, tk.END)
        self.entry_nom.delete(0, tk.END)
        self.var_obligatoire.set(True)

        self.groupes_temp.clear()
        self.reinitialiser_groupe(demander_confirmation=False)

    def ajouter_cours(self):
        sigle = self.entry_sigle.get().strip()
        nom = self.entry_nom.get().strip()
        obligatoire = self.var_obligatoire.get()

        if not sigle or not nom:
            messagebox.showerror("Erreur", "Tous les champs doivent être remplis.")
            return
        
        cours_existants = self.cours_obligatoires + self.cours_optionnels
        if any(c.nom.lower() == nom.lower() or c.sigle.lower() == sigle.lower() for c in cours_existants):
            messagebox.showerror("Erreur", f"Un cours ayant le sigle {sigle} ou le même nom {nom} à déjà été ajouté.")
            return

        cours = Cours(sigle, nom, obligatoire)
        for groupe in self.groupes_temp:
            cours.add_groupe(groupe)

        if obligatoire:
            self.cours_obligatoires.append(cours)
            self.liste_obligatoires.insert(tk.END, str(cours))
        else:
            self.cours_optionnels.append(cours)
            self.liste_optionnels.insert(tk.END, str(cours))

        self.reinitialiser_cours(demander_confirmation=False)

    def sauvegarder_cours(self, afficher_message=True):
        def cours_to_dict(c):
            return {
                "sigle": c.sigle,
                "nom": c.nom,
                "obligatoire": c.obligatoire,
                "groupes": [
                    {
                        "nom_groupe": g.nom_groupe,
                        "plages": g.plages
                    } for g in c.groupes
                ]
            }

        tous_les_cours = self.cours_obligatoires + self.cours_optionnels
        data = [cours_to_dict(c) for c in tous_les_cours]

        lecteur.sauvegarder_cours(data, afficher_message)

    def supprimer_cours(self):
        selection_obligatoire = self.liste_obligatoires.curselection()
        selection_optionnelle = self.liste_optionnels.curselection()

        if not selection_obligatoire and not selection_optionnelle:
            messagebox.showerror("Erreur", "Veuillez sélectionner un cours à supprimer.")
            return
        else:
            confirmation = self.demander_confirmation("Êtes-vous certain de vouloir supprimer ce cours? Cette action est irréversible.")
            if not confirmation:
                return

        if selection_obligatoire:
            index = selection_obligatoire[0]
            cours_a_supprimer = self.cours_obligatoires.pop(index)
            self.liste_obligatoires.delete(index)
        elif selection_optionnelle:
            index = selection_optionnelle[0]
            cours_a_supprimer = self.cours_optionnels.pop(index)
            self.liste_optionnels.delete(index)

        messagebox.showinfo("Succès", f"Le cours '{cours_a_supprimer.sigle} - {cours_a_supprimer.nom}' a été supprimé.")

    def reinitialiser_horaire(self):
        confirmation = self.demander_confirmation("Êtes-vous certain de vouloir supprimer tous les cours? Cette action est irréversible.")
        if not confirmation:
            return

        self.liste_obligatoires.delete(0, tk.END)
        self.cours_obligatoires.clear()

        self.liste_optionnels.delete(0, tk.END)
        self.cours_optionnels.clear()

        self.sauvegarder_cours(afficher_message=False)
        messagebox.showinfo("Réinitialisation", "Les cours ont tous été supprimés.")

    def initialiser_cours(self):
        cours_obligatoires, cours_optionnels = lecteur.charger_cours_depuis_fichier()

        for cours in cours_obligatoires:
            self.cours_obligatoires.append(cours)
            self.liste_obligatoires.insert(tk.END, str(cours))

        for cours in cours_optionnels:
            self.cours_optionnels.append(cours)
            self.liste_optionnels.insert(tk.END, str(cours))

    def demander_confirmation(self, message: str) -> bool:
        confirmation = messagebox.askyesno(
            "Confirmation",
            message
        )

        return confirmation