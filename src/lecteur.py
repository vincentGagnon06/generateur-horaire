"""
Auteur : Vincent Gagnon
Date : Juin 2025
Ce fichier permet de gérer les données contenues dans le fichier cours.json.
"""

import os
import json
from tkinter import messagebox
from generateur import Cours, GroupeHoraire

# Chemin du dossier cible
DOSSIER_COURS = os.path.expanduser("~/Downloads/GenerateurHoraire")
FICHIER_COURS = os.path.join(DOSSIER_COURS, "cours.json")

def _verifier_dossier():
    if not os.path.exists(DOSSIER_COURS):
        try:
            os.makedirs(DOSSIER_COURS)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de créer le dossier : {DOSSIER_COURS}\n\n{e}")

def charger_cours_depuis_fichier() -> tuple[list[Cours], list[Cours]]:
    _verifier_dossier()

    if not os.path.exists(FICHIER_COURS):
        # Créer un fichier JSON vide
        with open(FICHIER_COURS, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4, ensure_ascii=False)
        return [], []

    try:
        with open(FICHIER_COURS, "r", encoding="utf-8") as f:
            data = json.load(f)

        cours_obligatoires: list[Cours] = []
        cours_optionnels: list[Cours] = []

        for c in data:
            cours = Cours(
                sigle=c["sigle"],
                nom=c["nom"],
                obligatoire=c["obligatoire"]
            )
            for g in c["groupes"]:
                groupe = GroupeHoraire(g["nom_groupe"])
                groupe.plages = g["plages"]
                cours.add_groupe(groupe)

            if cours.obligatoire:
                cours_obligatoires.append(cours)
            else:
                cours_optionnels.append(cours)

        return cours_obligatoires, cours_optionnels

    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors du chargement de cours.json : {e}")
        return [], []

def sauvegarder_cours(data, afficher_message: bool) -> None:
    _verifier_dossier()

    try:
        with open(FICHIER_COURS, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        if afficher_message:
            messagebox.showinfo("Succès", f"Cours sauvegardés dans {FICHIER_COURS}")

    except Exception as e:
        messagebox.showerror("Erreur", f"Échec de la sauvegarde : {e}")