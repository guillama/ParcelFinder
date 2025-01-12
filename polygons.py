import math
import itertools

import pyproj

from json_parcel import Json
from shapely.geometry import Polygon


class PolygonCollection:
    """
       A collection of polygons (e.g., parcels or buildings) with operations for filtering and pairing.
    """
    def __init__(self, file_type: str):
        self.file_type = file_type
        self.polygon_list = []

    def __len__(self):
        return len(self.polygon_list)
    
    def __iter__(self):
        return iter(self.polygon_list)

    def __add__(self, other):
        new_collection = PolygonCollection(self.file_type)
        new_collection.polygon_list = self.polygon_list + other.polygon_list
        return new_collection

    # Download, extract, and parse GeoJSON files for a city, populating the collection with polygons.
    # Returns the list of parsed polygons.
    def parse_files(self, city_name):
        json = Json(city_name, self.file_type)
        file_gzip = json.download()
        files_json = json.extract(file_gzip)

        for file_path in files_json:
            for polygons in json.parse(file_path):
                for polygon in polygons:
                    p = MapPolygon(polygon)
                    self.polygon_list.append(p)

        return self.polygon_list

    # Filter polygons by area within a specified range.
    # Returns a new PolygonCollection with the filtered polygons.
    def from_area_range(self, area_min, area_max):
        filtered_polygons = [p for p in  self.polygon_list if area_min <= p.area() <= area_max]

        print(f"{len(filtered_polygons)} / {len( self.polygon_list)}")

        new_collection = PolygonCollection(self.file_type)
        new_collection.polygon_list = filtered_polygons

        return new_collection

    # Yield pairs of polygons from the current collection and another collection.
    def scan(self, other_collection):
        for parcel in self.polygon_list:
            for building in other_collection.polygon_list:
                yield parcel, building


class MapPolygon:
    """
        Represents a single polygon with geospatial properties and operations.
    """
    def __init__(self, coordinates: list):
        if coordinates[0] != coordinates[-1]:
            coordinates += [coordinates[0]]

        self.points = [tuple(c) for c in coordinates]
        self.polygon = Polygon(self.points)

    # Calculate the area of the polygon using a custom formula based on spherical geometry.
    # Returns the absolute area in square meters.
    def area2(self):
        def to_radian(angle):
            return angle * math.pi / 180

        def iter_points(collections):
            peeker, items = itertools.tee(collections)
            next(peeker)
            while 1:
                current = next(items)
                try:
                    next_val = next(peeker)
                except StopIteration:
                    return
                yield current, next_val

        area = 0
        for (x, y), (x2, y2) in iter_points(self.points):
            area += to_radian(x2 - x) * (2 + math.sin(to_radian(y)) + math.sin(to_radian(y2)))

        area *= 6378137 * 6378137 / 2

        return abs(area)

    # Calculate the geodesic area of the polygon using pyproj.
    # Returns the absolute area in square meters.
    def area(self):
        # Create a geodesic area calculator using pyproj
        geod = pyproj.Geod(ellps='GRS80')

        # Extract lats and lons
        lons = [x for x, y in self.points]
        lats = [y for x, y in self.points]

        # Calculate area using geodesic formulas
        area, _ = geod.polygon_area_perimeter(lons, lats)
        return abs(area)

    # Check if the polygon intersects with another polygon.
    def intersects(self, p):
        return self.polygon.intersects(p.polygon)

    # Returns the coordinates of the centroid.
    def centroid(self):
        return self.polygon.centroid.coords[0]

    # Check if the polygon completely contains another polygon.
    def contains(self, p):
        return self.polygon.contains(p.polygon)