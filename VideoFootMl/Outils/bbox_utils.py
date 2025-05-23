def getCentreBbox(bbox):
    """
        Calcule le centre d'une boîte englobante (bounding box).

        Paramètre :
            bbox : tuple (x1, y1, x2, y2) représentant les coins haut-gauche et bas-droit de la boîte.

        Retour :
            (x_centre, y_centre) : coordonnées du centre de la boîte
        """
    x1, y1, x2, y2 = bbox
    return int((x1 + x2) / 2), int((y1 + y2) / 2)


def mesure_Distance(p1, p2):
    """
        Calcule la distance euclidienne entre deux points p1 et p2.

        Paramètres :
            p1, p2 : tuples (x, y)

        Retour :
            distance : float
        """
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5


def getPositionPieds(bbox):
    """
        Calcule la position des pieds (milieu bas) d'une boîte englobante.

        Paramètre :
            bbox : tuple (x1, y1, x2, y2)

        Retour :
            (x_pied, y_pied) : coordonnées du point bas central
        """
    x1, y1, x2, y2 = bbox
    return int((x1 + x2) / 2), int(y2)


def mesureXYDistance(p1, p2):
    """
        Calcule la différence entre deux points p1 et p2 en x et y séparément.

        Paramètres :
            p1, p2 : tuples (x, y)

        Retour :
            (dx, dy) : différence en x et y
        """
    return p1[0] - p2[0], p1[1] - p2[1]


def getLargeurBbox(bbox):
    """
        Calcule la largeur d'une boîte englobante.

        Paramètre :
            bbox : tuple (x1, y1, x2, y2)

        Retour :
            largeur : int
        """
    return bbox[2] - bbox[0]
