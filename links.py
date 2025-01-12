class BingMapsLink:
    """
    Builds Bing Maps links for multiple latitude and longitude pairs.
    """
    URL_LIMIT = 100

    def __init__(self, longitudes, latitudes):
        self.longitudes = longitudes
        self.latitudes = latitudes
        self.coordinates_pairs = []

    def build_url(self):
        self.coordinates_pairs = list(zip(self.latitudes, self.longitudes))

        urls = []
        for i in range(0, len(self.coordinates_pairs), self.URL_LIMIT):
            url = self.build_url_from_index(i)
            urls.append(url)
        return urls

    def build_url_from_index(self, index):
        limit = min(index + self.URL_LIMIT, len(self.coordinates_pairs))
        url = "https://bing.com/maps/default.aspx?sp="
        for n, (lat, long) in enumerate(self.coordinates_pairs[index:limit], start=1):
            url += f"point.{lat:.5f}_{long:.5f}_{n}~"
            if n >= self.URL_LIMIT:
                break
        return url + "&style=h"
