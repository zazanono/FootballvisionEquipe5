def getCentreBbox(bbox):
    x1, y1, x2, y2 = bbox
    return int((x1 + x2) / 2), int((y1 + y2) / 2)


def measure_Distance(p1, p2):
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5


def getPositionPied(bbox):
    x1, y1, x2, y2 = bbox
    return int((x1 + x2) / 2), int(y2)


def mesure_XY_Distance(p1, p2):
    return p1[0] - p2[0], p1[1] - p2[1]


def getLargeurBbox(bbox):
    return bbox[2] - bbox[0]
