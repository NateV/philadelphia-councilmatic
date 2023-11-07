from django.core.management.base import BaseCommand, CommandError
import json
import sys
from philadelphia_scraper import DIVISION_ID




class Command(BaseCommand):
    """
    Transform philly's geojson with the properties councilmatic needs.

    See https://github.com/datamade/chi-councilmatic/blob/main/data/scripts/transform_shapes.py
    """
    help = "Adjust geojson from Philly's open Data portal to have the properties that councilmatic needs."

    def add_arguments(self, parser):
        parser.add_argument(
                "geojson",
                type=str,
                help="path to geojson file"
                )
        parser.add_argument(
                "output",
                type=str,
                help="path to output file."
                )

    def handle(self, *args, geojson="", output="", **kwargs):
        print("Transforming %s" % geojson)
        assert geojson != ""
        assert output != ""
        with open(geojson, "r") as inpt, open(output, "w") as out:
            boundaries = json.load(inpt)
            for feature in boundaries['features']:
    
                division_id = f"{DIVISION_ID}/council_district:{feature['properties']['DISTRICT']}"
                    
                print("processing %s", division_id)
                feature['properties']['division_id'] = division_id
            
            json.dump(boundaries, out)
