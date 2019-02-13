from geopy import distance


def correction(lat, lon, dwt):
    c = (59.878635, 30.196835) #угольная гавань
    n = (lat, lon)
    d = distance.distance(n, c).kilometers
    if d > 7000 and dwt < 7000:
        return 30
    if d < 3500:
        return 0
    else:
        return int(d/500)-5
