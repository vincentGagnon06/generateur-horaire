"""
Auteur : Vincent Gagnon
Date : Juin 2025
Ce fichier contient les fonctions permettant d'afficher et de gérer l'interface d'ajouts de cours.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from generateur import Cours, GroupeHoraire
import lecteur
from exceptions import MinuteInvalideError, HeureHorsLimitesError, ValeurNonEntreeError

class FenetreGeneration(tk.Frame):
    def __init__(self, master, changer_fenetre):
        super().__init__(master)
        self.changer_fenetre = changer_fenetre

        self.cours_obligatoires = []
        self.cours_optionnels = []
        self.groupes_temp = {}

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
        self.entree_sigle = entry(0)
        label(1, "Nom:")
        self.entree_nom = entry(1)

        self.var_obligatoire = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Obligatoire", variable=self.var_obligatoire).grid(row=2, column=0, columnspan=2)
        ttk.Separator(frame, orient="horizontal").grid(row=3, column=0, columnspan=2, sticky="ew", pady=5)

        label(4, "Nom du groupe:")
        self.entree_nom_groupe = entry(4)

        self.frame_plages = ttk.LabelFrame(frame, text="Plages horaires")
        self.frame_plages.grid(row=5, column=0, columnspan=2, sticky="ew", pady=5)
        self.frame_plages.columnconfigure((0, 1, 2), weight=1)

        for i, t in enumerate(["Jour", "Début", "Fin"]):
            ttk.Label(self.frame_plages, text=t).grid(row=0, column=i)

        self.lignes_plages = []
        ttk.Button(self.frame_plages, text="Ajouter une ligne", command=self.ajouter_ligne_plage).grid(row=999, column=0, columnspan=3, pady=3)

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

        ttk.Label(frame, text="Nombre de cours optionnels:").grid(row=0, column=0, sticky="e")
        self.entree_nb_cours_option = ttk.Entry(frame)
        self.entree_nb_cours_option.grid(row=0, column=1, sticky="ew")

        ttk.Button(frame, text="Générer les horaires", command=self.generer_horaires).grid(row=1, column=0, columnspan=2, pady=(0, 10))

    def generer_horaires(self):
        try:
            nb_cours_optionnels = int(self.entree_nb_cours_option.get().strip())
            if not 0 <= nb_cours_optionnels <= len(self.cours_optionnels):
                raise ValueError("Nombre hors limites")
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
        jour = ttk.Entry(self.frame_plages, justify="center")
        debut = ttk.Entry(self.frame_plages, justify="center")
        fin = ttk.Entry(self.frame_plages, justify="center")

        jour.grid(row=row, column=0, sticky="ew", padx=2, pady=1)
        debut.grid(row=row, column=1, sticky="ew", padx=2, pady=1)
        fin.grid(row=row, column=2, sticky="ew", padx=2, pady=1)

        self.lignes_plages.append((jour, debut, fin))

    def reinitialiser_groupe(self):
        confirmation = self.demander_confirmation("Êtes-vous certain de vouloir supprimer ce groupe? Cette action est irréversible.")
        if not confirmation:
            return

        self.entree_nom_groupe.delete(0, tk.END)
        for e in self.lignes_plages:
            for champ in e:
                champ.destroy()
        self.lignes_plages.clear()

    def ajouter_groupe(self):
        def parse_heure(valeur):
            valeur = valeur.strip() 
            
            try:
                if valeur == "":
                    raise ValeurNonEntreeError("Valeur non entrée")

                if ":" in valeur or "h" in valeur:
                    splitChar = ":" if ":" in valeur else "h"
                    heures, minutes = map(int, valeur.split(splitChar))
                    
                    sHeures, sMinutes = valeur.split(splitChar)
                    if len(sHeures) > 2 or len(sMinutes) != 2:
                        raise ValueError("Longueurs invalides")
                        
                    if not 0 <= minutes < 60:
                        raise MinuteInvalideError("Minutes invalides")

                    if not 8 <= heures + minutes / 60 <= 20:
                        raise HeureHorsLimitesError("Heure hors limites")
                    return heures + minutes / 60
                else:
                    heure_float = float(valeur)
                    if not 8 <= heure_float <= 20:
                        raise HeureHorsLimitesError("Heure hors limites")
                    return heure_float
                
            except MinuteInvalideError:
                messagebox.showerror("Erreur", "Veuillez entrer des minutes entre 0 et 60.")   
            except ValeurNonEntreeError:
                messagebox.showerror("Erreur", "Veuillez entrer une heure de début et de fin.")
            except HeureHorsLimitesError:
                messagebox.showerror("Erreur", "L'heure doit être comprise entre 8h et 20h.")
            except (ValueError, TypeError):
                messagebox.showerror("Erreur", "Format invalide pour l'heure (attendu HH:MM en format 24h ou seulement l'heure)")

        nom = self.entree_nom_groupe.get().strip()
        if not nom:
            messagebox.showerror("Erreur", "Le nom du groupe est requis.")
            return

        if nom in self.groupes_temp:
            messagebox.showerror("Doublon", f"Un groupe nommé « {nom} » a déjà été ajouté à ce cours.")
            return

        groupe = GroupeHoraire(nom)

        for jour_e, debut_e, fin_e in self.lignes_plages:
            jour = jour_e.get().strip().lower()
            jours = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
            if jour not in jours:
                messagebox.showerror("Erreur", "Le jour entré est invalide.")
                return

            debut = parse_heure(debut_e.get())
            if debut is None:
                return

            fin = parse_heure(fin_e.get())
            if fin is None:
                return
            
            if debut >= fin:
                messagebox.showerror("Erreur", "L'heure de début doit être inférieure à l'heure de fin.")
                return
            
            groupe.plages.append((jour, debut, fin))

        if not groupe.plages:
            messagebox.showerror("Erreur", "Aucune plage horaire définie pour ce groupe.")
            return

        self.groupes_temp[nom] = groupe
        messagebox.showinfo("Ajouté", f"Groupe {nom} ajouté au cours.")
        self.entree_nom_groupe.delete(0, tk.END)
        self.label_groupes_temp.config(text=f"Groupes ajoutés : {len(self.groupes_temp)}")

        # Nettoyage
        for e in self.lignes_plages:
            for champ in e:
                champ.destroy()
        self.lignes_plages.clear()

    def reinitialiser_cours(self):
        confirmation = self.demander_confirmation("Êtes-vous certain de vouloir supprimer tous les groupes de ce cours? Cette action est irréversible.")
        if not confirmation:
            return

        self.entree_sigle.delete(0, tk.END)
        self.entree_nom.delete(0, tk.END)
        self.var_obligatoire.set(True)

        self.groupes_temp.clear()
        self.label_groupes_temp.config(text="Groupes ajoutés : 0")

        self.entree_nom_groupe.delete(0, tk.END)
        for e in self.lignes_plages:
            for champ in e:
                champ.destroy()
        self.lignes_plages.clear()

    def ajouter_cours(self):
        sigle = self.entree_sigle.get().strip()
        nom = self.entree_nom.get().strip()
        obligatoire = self.var_obligatoire.get()

        if not sigle or not nom:
            messagebox.showerror("Erreur", "Tous les champs doivent être remplis.")
            return

        for cours in self.cours_obligatoires + self.cours_optionnels:
            if cours.sigle.lower() == sigle.lower():
                messagebox.showerror("Doublon", f"Un cours avec le sigle « {sigle} » existe déjà.")
                return
            if cours.nom.lower() == nom.lower():
                messagebox.showerror("Doublon", f"Un cours avec le nom « {nom} » existe déjà.")
                return

        cours = Cours(sigle, nom, obligatoire)
        for groupe in self.groupes_temp.values():
            cours.add_groupe(groupe)

        if obligatoire:
            self.cours_obligatoires.append(cours)
            self.liste_obligatoires.insert(tk.END, str(cours))
        else:
            self.cours_optionnels.append(cours)
            self.liste_optionnels.insert(tk.END, str(cours))

        # Réinitialisation
        self.entree_sigle.delete(0, tk.END)
        self.entree_nom.delete(0, tk.END)
        self.var_obligatoire.set(True)
        self.groupes_temp.clear()
        self.label_groupes_temp.config(text="Groupes ajoutés : 0")

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