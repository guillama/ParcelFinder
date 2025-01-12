import csv
import shutil
import gzip
import json

from urllib.request import urlretrieve
from pathlib import Path


class Json:
    """
       Handles downloading, extracting, and parsing GeoJSON files for a city.
    """
    INSEE_FILENAME = "insee_code.csv"
    BASE_URL = "https://cadastre.data.gouv.fr/data/etalab-cadastre/" \
               "latest/geojson/communes/"
    INPUT_DIR = Path("./inputs")

    def __init__(self, city_name, file_type):
        self.city_name = city_name
        self.file_type = file_type

    # Download GeoJSON files for the specified city and type, based on INSEE codes.
    # Returns a dictionary mapping INSEE codes to downloaded file paths.
    def download(self):
        insee_codes = self.city_to_insee(self.city_name)

        downloaded_files = {}
        for n, code in enumerate(insee_codes, start=1):
            url = self.build_parcel_link(code, self.file_type)
            filepath = Path(f"/tmp/{code}-{self.file_type}-{n}.json.gz")
            downloaded_files.setdefault(code, []).append(filepath)

            dest_path = self.INPUT_DIR / Path(filepath).stem
            if dest_path.exists():
                continue

            print(f"Downloading {code} {self.file_type} JSON file...")
            print(f"{url} -> {filepath}")
            urlretrieve(url, filepath)

        return downloaded_files

    # Convert a city name to its corresponding INSEE codes using a CSV file.
    # Returns a set of INSEE codes.
    def city_to_insee(self, city):
        insee_codes = set()
        with (open(self.INSEE_FILENAME, encoding="iso-8859-1") as csvfile):
            insee = csv.DictReader(csvfile, delimiter=';')
            for row in insee:
                code_insee, ville, code_postal, *_ = row.values()
                if city.upper() == ville:
                    insee_codes.add(code_insee)

        if not insee_codes:
            print(f"Error: INSEE code for city: {city} not found.")

        return insee_codes

    # Build the download URL for a cadastre file based on the INSEE code and file type.
    def build_parcel_link(self, code, filetype: str):
        departement = code[:2]
        return self.BASE_URL + f"{departement}/{code}/" \
                               f"cadastre-{code}-{filetype}.json.gz"

    # Extract gzipped JSON files to a specified directory.
    # Returns a list of paths to the extracted files.
    def extract(self, files: dict):
        if not self.INPUT_DIR.exists():
            Path.mkdir(self.INPUT_DIR)

        extracted_files = []
        for n, (code, source_files) in enumerate(files.items(), start=1):
            for src in source_files:
                dest_path = self.INPUT_DIR / Path(src).stem
                extracted_files.append(dest_path)

                if dest_path.exists():
                    continue

                print(f"Extracting {src} -> {dest_path}...")
                with gzip.open(src, 'rb') as gzipfile:
                    with open(dest_path, 'wb') as jsonfile:
                        shutil.copyfileobj(gzipfile, jsonfile)

        return extracted_files

    # Parse a GeoJSON file to yield polygon coordinates for each feature.
    @staticmethod
    def parse(file):
        with open(file, "r") as f:
            json_polygons = json.load(f)

        for features in json_polygons.get("features", []):
            geometry = features.get("geometry", {})
            if geometry["type"] == "MultiPolygon":
                for coordinates in geometry.get("coordinates", []):
                    yield coordinates
            elif geometry["type"] == "Polygon":
                yield geometry.get("coordinates", [])
            else:
                raise ValueError("Unexpected geometry type from JSON file")