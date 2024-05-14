from django.core.management.base import BaseCommand, CommandError
import json
import sys
from philadelphia.models import (
   PhilaBill )
from councilmatic_core.models import (
   Membership,
   Event,
   Bill,
   Person,
   Post)




class Command(BaseCommand):
    """
    Clean the database, removing models, so that we can 
    re-scrape.
    """
    help = "Clean the database. Remove models so that we can re-scrape."

    def add_arguments(self, parser):
        parser.add_argument(
                "--forreal",
                action="store_false",
                dest="forreal",
                default=True, 
                help="Really delete? By default, we just see what _would_ get deleted")

    def handle(self, *args, forreal=True, **kwargs):
        #classes = [PhilaBill, Person, Event, Membership]
        classes = [Person, Membership]

        for thisclass in classes:
            objs = thisclass.objects.all()
            print(f"Deleting {len(objs)} {thisclass.__name__}s.")
            if forreal==True:
                print("Not actually deleting")
                continue
            # only actually delete things if dryrun
            # is false.
            print("ACTUALLY DELETING")
            for obj in objs:
                obj.delete()

