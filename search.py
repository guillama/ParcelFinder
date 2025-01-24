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

