from sklearn.cluster import KMeans

class CouleurEquipe:
    def __init__(self):
        self.couleur_equipe = {}
        self.equipes_joueurs_dict = {}

    def get_couleur_joueur(self, frame, bbox):
        # enforce that bbox unpacks to exactly four coords
        try:
            x1, y1, x2, y2 = bbox
        except Exception:
            raise ValueError(f"Expected bbox to be a 4-tuple/list of numbers, got {bbox!r} (type={type(bbox)})")

        # crop and split
        crop = frame[int(y1):int(y2), int(x1):int(x2)]
        moitie_haut = crop[: crop.shape[0] // 2, :]

        # cluster the top half into player vs. background
        kmeans_fg_bg = self.get_model_groupage(moitie_haut)
        labels = kmeans_fg_bg.labels_.reshape(moitie_haut.shape[:2])

        # pick the “background” label by looking at the four corners
        corners = [labels[0, 0], labels[0, -1], labels[-1, 0], labels[-1, -1]]
        bg_label = max(set(corners), key=corners.count)
        player_label = 1 - bg_label

        # return the RGB center of the “player” cluster
        return kmeans_fg_bg.cluster_centers_[player_label]

    # def get_couleur_joueur(self, frame, bbox):
    #
    #     print("DEBUG get_couleur_joueur got bbox:", bbox, "(", type(bbox), ")")
    #
    #     image = frame[int(bbox[1]):int(bbox[3]),int(bbox[0]):int(bbox[2])]
    #     moitie_haut = image[0:int(image.shape[0]/2),:]
    #
    #     # Model de groupage
    #     kmeans = self.get_model_groupage(moitie_haut)
    #
    #     # get les labels des groupes
    #     labels = kmeans.labels_
    #
    #     # Reformer pour correspondre à l'image de base
    #     images_groupees = labels.reshape(moitie_haut.shape[0], moitie_haut.shape[1])
    #
    #     groupe_coins = [images_groupees[0, 0], images_groupees[0, -1], images_groupees[-1, 0], images_groupees[-1, -1]]
    #     groupe_nonjoueurs = max(set(groupe_coins), key=groupe_coins.count)
    #     print(groupe_nonjoueurs)
    #
    #     groupe_joueurs = 1-groupe_nonjoueurs
    #     print(groupe_joueurs)
    #
    #     couleur_joueur = kmeans.cluster_centers_[groupe_joueurs]
    #
    #     return couleur_joueur
    #

    def assignation_couleur(self, frame, detections_joueurs):
        couleurs_joueurs = []
        for id_joueur, detection_joueur in detections_joueurs.items():
            bbox = detection_joueur.get('bbox')
            print(f"DEBUG assignation_couleur: id_joueur={id_joueur}, bbox={bbox!r} ({type(bbox)})")
            # enforce it’s a 4-tuple/list
            try:
                x1, y1, x2, y2 = bbox
            except Exception:
                raise ValueError(f"[assignation_couleur] expected 4-tuple bbox, got {bbox!r}")
            couleur_joueur = self.get_couleur_joueur(frame, bbox)
            couleurs_joueurs.append(couleur_joueur)

        kmeans = KMeans(n_clusters=2, init="k-means++", n_init=1)
        kmeans.fit(couleurs_joueurs)
        self.kmeans = kmeans
        self.couleur_equipe = {
            1: kmeans.cluster_centers_[0],
            2: kmeans.cluster_centers_[1],
        }

    # def assignation_couleur(self, frame, detections_joueurs):
    #
    #     couleurs_joueurs = []
    #     for _, detection_joueur in detections_joueurs.items():
    #         bbox = detection_joueur['bbox']
    #         couleur_joueur = self.get_couleur_joueur(frame, bbox)
    #         couleurs_joueurs.append(couleur_joueur)
    #
    #     kmeans = KMeans(n_clusters=2, init="k-means++", n_init=1)
    #     kmeans.fit(couleurs_joueurs)
    #
    #     self.kmeans = kmeans
    #
    #     self.couleur_equipe[1] = kmeans.cluster_centers_[0]
    #     self.couleur_equipe[2] = kmeans.cluster_centers_[1]

    def get_model_groupage(self, moitie_haut):
       # Image -> tableau 2d
       image_2d = moitie_haut.reshape(-1,3)

       # Faire le groupage
       kmeans = KMeans(n_clusters=2, init="k-means++", n_init=1)
       kmeans.fit(image_2d)

       return kmeans

    def get_equipe_joueur(self, frame, bbox, id_joueur):
        print(f"DEBUG get_equipe_joueur call: id_joueur={id_joueur}, bbox={bbox!r} ({type(bbox)})")
        # if we’ve already assigned, just return
        if id_joueur in self.equipes_joueurs_dict:
            return self.equipes_joueurs_dict[id_joueur]

        # enforce bbox shape
        try:
            x1, y1, x2, y2 = bbox
        except Exception:
            raise ValueError(f"[get_equipe_joueur] expected 4-tuple bbox, got {bbox!r}")

        # now get the player’s color and predict team
        couleur_joueur = self.get_couleur_joueur(frame, bbox)
        team_idx = self.kmeans.predict(couleur_joueur.reshape(1, -1))[0] + 1

        self.equipes_joueurs_dict[id_joueur] = team_idx
        return team_idx

    # def get_equipe_joueur(self, frame, bbox, id_joueur):
    #     if id_joueur in self.equipes_joueurs_dict:
    #         return self.equipes_joueurs_dict[id_joueur]
    #
    #     couleur_joueur = self.get_couleur_joueur(frame, bbox)
    #
    #     id_equipe = self.kmeans.predict(couleur_joueur.reshape(1,-1))[0]
    #     id_equipe += 1
    #
    #     self.equipes_joueurs_dict[id_joueur] = id_equipe
    #
    #     return id_equipe