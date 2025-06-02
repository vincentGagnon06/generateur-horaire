class Cours:
    def __init__(self, sigle, nom, obligatoire=True):
        self.sigle = sigle
        self.nom = nom
        self.groupes = []
        self.obligatoire = obligatoire

    def add_groupe(self, groupe):
        self.groupes.append(groupe)
        groupe.cours = self

    def __str__(self):
        groupes_str = ", ".join(g.nom_groupe for g in self.groupes)
        return f"{self.sigle} - {self.nom} : ({groupes_str})"

class GroupeHoraire:
    def __init__(self, nom_groupe):
        self.cours = None
        self.nom_groupe = nom_groupe
        self.plages: list[tuple[str, float, float]] = []

    def __str__(self):
        plages_str = ", ".join(
            f"{jour} {debut:.2f}-{fin:.2f}" for jour, debut, fin in self.plages
        )
        return f"{self.nom_groupe} : {plages_str}"

class Generateur:
    def __init__(self, cours_obligatoires, cours_optionnels, nb_cours_optionnels):
        self.cours_obligatoires: list[Cours] = cours_obligatoires
        self.cours_optionnels: list[Cours] = cours_optionnels
        self.nb_cours_optionnels: int = nb_cours_optionnels

        self.horaires: list[list[GroupeHoraire]] = []      
    
    def creer_horaires(self):
        combinaisons: list[list[Cours]] = []

        #Initialise toutes les combinaisons de cours possibles
        combinaisons_options: list[list[Cours]] = self.combinaisons_cours_options()
        for combinaison_option in combinaisons_options:
            combinaison = []
            combinaison.extend(self.cours_obligatoires)
            combinaison.extend(combinaison_option)

            combinaisons.append(combinaison)

        #Creer les horaires en choisisant les groupes
        for combinaison in combinaisons:
            self.creer_horaires_from_combinaison(combinaison, list())

        self.filtrer_horaires()

    def combinaisons_cours_options(self) -> list[list[Cours]]:
        combinaisons: list[list[Cours]] = []

        for i in range(2 ** len(self.cours_optionnels)):
            current_optionnels: list[Cours] = []
            for j in range(len(self.cours_optionnels)):
                binary_at_index = (i >> j) & 1
                if bool(binary_at_index):
                    current_optionnels.append(self.cours_optionnels[j])

            if len(current_optionnels) == self.nb_cours_optionnels:
                combinaisons.append(current_optionnels)
        
        return combinaisons

    def creer_horaires_from_combinaison(self, combinaison: list[Cours], groupes: list[GroupeHoraire]):
        if len(combinaison) == 0:
            self.horaires.append(groupes)
            return

        cours = combinaison[0]
        for groupe in cours.groupes:
            nouveaux_groupes = groupes.copy()
            nouveaux_groupes.append(groupe)
            self.creer_horaires_from_combinaison(combinaison[1:], nouveaux_groupes)

    def filtrer_horaires(self):
        def add_to_occupe(plage) -> bool:
            nonlocal occupe

            jour, debut, fin = plage
            if jour not in occupe:
                occupe[jour] = []

            for d, f in occupe[jour]:
                if not (fin <= d or debut >= f):
                    return False 

            occupe[jour].append((debut, fin))
            return True

        horaires_filtres = []

        for horaire in self.horaires:
            occupe: dict[str, list[tuple[float, float]]] = dict() #Jour avec toutes les plages horaires occupées
            valide = True

            for groupe in horaire:
                for plage in groupe.plages:
                    libre = add_to_occupe(plage)
                    if not libre:
                        valide = False
                        break
                if not valide:
                    break

            if valide:
                horaires_filtres.append(horaire)

        self.horaires = horaires_filtres