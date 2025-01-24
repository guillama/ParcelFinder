import pyproj

from json_parcel import Json


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
            for shapely_poly in json.parse(file_path):
                p = MapPolygon(shapely_poly)
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
    def __init__(self, polygon):
        self.polygon = polygon

    # Calculate the geodesic area of the polygon using pyproj.
    # Returns the absolute area in square meters.
    def area(self):
        geod = pyproj.Geod(ellps='GRS80')

        # Calculate exterior area
        exterior_coords = self.polygon.exterior.coords
        lons = [x for x, y in exterior_coords]
        lats = [y for x, y in exterior_coords]
        total_area, _ = geod.polygon_area_perimeter(lons, lats)

        # Subtract interior areas (holes)
        for interior in self.polygon.interiors:
            interior_coords = interior.coords
            lons_hole = [x for x, y in interior_coords]
            lats_hole = [y for x, y in interior_coords]
            hole_area, _ = geod.polygon_area_perimeter(lons_hole, lats_hole)
            total_area -= hole_area

        return abs(total_area)

    # Check if the polygon intersects with another polygon.
    def intersects(self, p):
        return self.polygon.intersects(p.polygon)

    # Returns the coordinates of the centroid.
    def centroid(self):
        return self.polygon.centroid.coords[0]

    # Check if the polygon completely contains another polygon.
    def contains(self, p):
        return self.polygon.contains(p.polygon)