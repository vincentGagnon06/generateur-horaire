class HeureHorsLimitesError(Exception):
    """Exception levée lorsque l'heure est en dehors de la plage autorisée (8h à 19h)."""
    pass

class ValeurNonEntreeError(Exception):
    """Exception levée quand aucune valeur n’a été entrée."""
    pass

class MinuteInvalideError(Exception):
    """Exception levée quand les minutes entrées ne sont pas comprises entre 0 et 60."""
    pass