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

            buildings = matches[parcel_key]
            buildings_areas = [b.area() for b in matches[parcel_key]]
            buildings_areas.sort(reverse=True)

            buildings_areas_str = ["%.0f" % a for a in buildings_areas]
            long, lat = buildings[0].centroid()
            print(f"{1 + (index % 100)}: {area:.1f} m2, buildings: {buildings_areas_str} m2 -> ({long:.5f}, {lat:.5f})")

        print('-' * 100)

        buildings = [b[0] for b in matches.values() if b]
        building_centroids = [b.centroid() for b in buildings]
        longitudes, latitudes = zip(*building_centroids)

        for url in BingMapsLink(longitudes, latitudes).build_url():
            print(url)

        print(f"matches: {len(matches)}")
