import argparse

from polygons import PolygonCollection
from search import ParcelBuildingSearch

FILETYPE_PARCELS = "parcelles"
FILETYPE_BUILDINGS = "batiments"


class Main:
    """
        Main class to manage and execute the land search process.
    """
    def __init__(self):
        self.city_name = ""
        self.target_area = 0
        self.area_precision = 1
        self.min_building_size = 0

    # Parse command-line arguments and initialize parameters for the search.
    def parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('city_name')
        parser.add_argument('target_area', type=int)
        parser.add_argument("-p", "--area_precision", type=int, default=0)
        parser.add_argument("-s", "--min_building_size", dest="min_building_size", type=int, default=0)
        parser.parse_args(namespace=self)

    # Execute the search
    def run(self):
        print(f"Searching land with area : {self.target_area} m2...")
        self.standard_search()

    # Perform a standard search to find parcels and buildings matching the criteria.
    def standard_search(self):
        parcels = PolygonCollection(FILETYPE_PARCELS)
        parcels.parse_files(self.city_name)
        match_parcels = parcels.from_area_range(self.target_area, self.target_area + self.area_precision)

        buildings = PolygonCollection(FILETYPE_BUILDINGS)
        buildings.parse_files(self.city_name)
        match_buildings = buildings.from_area_range(self.min_building_size, self.target_area)

        search = ParcelBuildingSearch(match_parcels, match_buildings)
        search.find_building_matches()
        search.display_results()


def main():
    m = Main()
    m.parse_args()
    m.run()


if __name__ == '__main__':
    main()
