from polygons import PolygonCollection
from collections import defaultdict
from links import BingMapsLink

from tqdm import tqdm


class ParcelBuildingSearch:
    def __init__(self, parcel_collection: PolygonCollection, building_collection: PolygonCollection):
        self.parcels = parcel_collection
        self.buildings = building_collection
        self.parcel_to_buildings = defaultdict(list)

    def find_building_matches(self):
        """
        Finds buildings contained within each parcel.
        """
        total_comparisons = len(self.parcels) * len(self.buildings)
        with tqdm(total=total_comparisons) as pbar:
            for parcel, building in self.parcels.scan(self.buildings):
                pbar.update(1)
                if parcel.contains(building):
                    self.parcel_to_buildings[(parcel, parcel.area())].append(building)


    def display_results(self):
        """
        Displays the search results, including parcel areas, matching building areas,
        and centroid coordinates.
        Outputs Bing Maps URLs with all building centroids.
        """
        print('-' * 100)

        matches = self.parcel_to_buildings

        for index, parcel_key in enumerate(matches.keys()):
            _, area = parcel_key

            # Sort buildings list by size (biggest first), then update the dictionary value
            buildings_areas = [(b.area(), b) for b in matches[parcel_key]]
            buildings_areas.sort(reverse=True)
            matches[parcel_key] = [b for (_area, b) in buildings_areas]

            _area, biggest_building = buildings_areas[0]
            long, lat = biggest_building.centroid()

            buildings_areas_str = ["%.0f" % a for (a, _) in buildings_areas]
            print(f"{1 + (index % 100)}: {area:.1f} m2, buildings: {buildings_areas_str} m2 -> ({long:.5f}, {lat:.5f})")

        print('-' * 100)

        # Get the first element of the previously sorted list of biggest buildings
        buildings = [b[0] for b in matches.values() if b]
        building_centroids = [b.centroid() for b in buildings]
        longitudes, latitudes = zip(*building_centroids)

        for url in BingMapsLink(longitudes, latitudes).build_url():
            print(url)

        print(f"matches: {len(matches)}")


class CombineSearch:
    def __init__(self, parcels: PolygonCollection, buildings: PolygonCollection, area):
        self.parcels = parcels
        self.buildings = buildings
        self.matches = defaultdict(list)
        self.area = area

        self.parcels_free = set()
        self.parcels_withbuilding = dict()

    def search(self):
        for parcel in self.parcels:
            if not self.search_for_building(parcel):
                self.parcels_free.add(parcel)

        for parcel in self.parcels_withbuilding.keys():
            for parcel_free in self.parcels_free:
                area = parcel.area() + parcel_free.area()
                if (self.area - 25) <= area <= (self.area + 25):
                    if parcel.intersects(parcel_free):
                        building = self.parcels_withbuilding[parcel]
                        self.matches[(parcel, parcel_free, area)].append(building)


    def search_for_building(self, parcel):
        for building in self.buildings:
            if building.area() > 50 and parcel.contains(building):
                self.parcels_withbuilding[parcel] = building
                return True

        return False

    def show(self):
        print('-' * 100)

        matches = self.matches

        for index, key in enumerate(matches.keys()):
            _, _, area = key

            buildings = matches[key]
            buildings_areas = [(b, b.area()) for b in buildings]
            buildings_areas.sort(reverse=True)
            biggest_building, _ = buildings_areas[0]
            long, lat = biggest_building.centroid()

            buildings_areas = ["%.0f" % a for a in buildings_areas]
            print(f"{1 + (index % 100)}: {area:.1f} m2, buildings: {buildings_areas} m2 -> ({long:.5f}, {lat:.5f})")

        print('-' * 100)

        if matches:
            buildings = [b[0] for b in matches.values() if b]
            gps = [b.centroid() for b in buildings]
            longitudes, latitudes = zip(*gps)
            for url in BingMapsLink(longitudes, latitudes).build_url():
                print(url)

        print(f"matches: {len(matches)}")