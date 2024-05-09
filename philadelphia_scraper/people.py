from pupa.scrape import Scraper
from pupa.scrape import Person
from pupa.scrape import Organization
import lxml
import re
import logging
import json 
from datetime import date
from typing import List, Tuple
from philadelphia_scraper.utils import (
        name_adjuster,
        from_x,
        get_last_name,
        pad_list
        )

logger = logging.getLogger(__name__)

# TODO figure out current term official start and end dates
CURRENT_TERM_START="2024-01-01"
CURRENT_TERM_END="2024-12-31"

def find_any_matching_extra_person(person: Person, others: List[Person]) -> Tuple[Person|None, List[Person]]:
    """
    Find if there's a person in 'others' that seems to be the sam
    person as person. 

    if so, split them out of the list of persons.

    """
    for idx, p in enumerate(others):
        if person.name.lower().strip() == p.name.lower().strip():
            return p, others[:idx] + others[idx+1:]
    return None, others

def merge_people(match: Person, person: Person):
    """
    Given two people with the same name, merge _certain_ properties of 'match' into 'person'.

    This doesn't merge terms, for example.
    """
    person.family_name = match.family_name
    person.other_names.extend(match.other_names)

    return person


class PhiladelphiaPersonScraper(Scraper):

    """
    Philadelphia's Legistar instance seems to not have pages dedicated to the legislators. This seems to be fairly common. Other sites have the info about who is on city council.

    See the municpal_scrapers for boise, denver, rialto, for examples of other scrapers that find 
    legislators from other sites.
    """

    # TODO this should not have a trailing /
    COUNCIL_ROOT = "https://phlcouncil.com/"
    COUNCIL_URL = "https://phlcouncil.com/council-members"


    def scrape(self):


        council = Organization('Philadelphia City Council', classification="legislature")
        council.add_source(self.COUNCIL_ROOT)
        yield council

        # nb. the . at the start of each path makes the search relative.
        name_xpath = ".//h4[@class='x-face-title']/strong"
        # where the data is written on front and back of the card, pick one.
        subtitle_xpath = ".//div[@class='x-face-outer front']//p[@class='x-face-text']/strong/big" # the 'Whip' or 'Leader' title, if any. 
        district_xpath = ".//div[@class='x-face-outer front']//p[@class='x-face-text']/strong" # district, not the 'Whip' or 
        link_xpath = ".//a[@class='x-face-button']/@href"
        pic_path = ".//div[@class='x-face-graphic']/img/@src"


        response = self.request(url=self.COUNCIL_URL, method="GET")

        html = response.text
        doc = lxml.html.fromstring(html)
            
 
        # philly's council site has members on 'cards'. We'll iterate over each card to make sure
        # we catch those that are vacant and keep all the data points together.
        cards_path = "//div[@class='x-card-inner']"
        cards = doc.xpath(cards_path)


        # If there's a former member who is still listed in committees and hearings,
        # then we still need to add that person to the database, even if they're 
        # no longer listed as a council member. 
        # This extra_people.json file gives us a mechanism for just adding former 
        # members by hand.
        # Its also useful for collecting people by hand who have commonly misspelled
        # names. Or typographical issues like inconsistent use of ' versus ’
        with open("philadelphia_scraper/extra_people.json","r") as extra_people_file:
            extra_people = list()
            extra_data_dict = json.load(extra_people_file)
            for extra_person_record in extra_data_dict["people"]:
                extra_p = Person(
                        extra_person_record['name'],
                        image=extra_person_record.get('image'))
                extra_p.family_name = extra_person_record.get('family_name')

                extra_p.add_source(self.COUNCIL_URL)

                for term_record in extra_person_record.get("terms") or []:
                    extra_p.add_term(
                        role=term_record["role"],
                        org_classification=term_record["org_classification"],
                        label=term_record["label"],
                        district=term_record["district"],
                        start_date=term_record.get("start_date"),
                        end_date=term_record["end_date"]
                        )

                for addl_name in extra_person_record.get('additional_names') or []:
                    extra_p.add_name(addl_name)
                extra_people.append(extra_p)



        for card_num, card in enumerate(cards):


            
            name = from_x(card.xpath(name_xpath)).title()
            if re.search("vacant",name, flags=re.I): 
                continue
            url = from_x(card.xpath(link_xpath))
            url = f"{self.COUNCIL_ROOT}{url}"
            subtitle = from_x(card.xpath(subtitle_xpath))
            pic = from_x(card.xpath(pic_path))
            dist_pat = re.compile(r"^DISTRICT (?P<distnum>\d+)$")
            district = from_x(card.xpath(district_xpath))
            last_name = get_last_name(name)

            # Create legislator.
            
            # BUG seems like I should't put the district here, because I add a 
            # term later...
            #person = Person(name_adjuster(name), image=pic, district=district)
            
            person = Person(name_adjuster(name), image=pic)

            # I don't know what to do for names that have family name as not last.
            # We need the family name because legislation is linked to people in legistar only by 'CouncilMember [last name]'.
            person.family_name = last_name
            # use add_name to add Councilmember xxx so that pupa will be able 
            # to tell that "Councilmember xxx" refers to the right person.
            person.add_name(f"Councilmember {last_name}")
            
            if re.search("’",person.family_name):
                #the name has a curly apostrophe in it, and we want to be able to 
                # match them if their name is recorded with a '
                # which is what Legistar does.
                alt_family_name = re.sub("’",person.family_name,"'")
                person.add_name(f"Councilmember {alt_family_name}")

                alt_name = re.sub("’",person.name,"'")
                person.add_name(alt_name)

            # Add membership on council.
            # is this a mistake, since we're also adding roles?
            #person.add_membership(council)

            # add terms of office. I think this is where the site picks up that Joe is the Dist
            # 1 Council member. 


            

            match = dist_pat.match(district or "")

            if match:
                dist_num = match.group('distnum')


            else:
                logger.warn("unknown district pattern for %s: %s", name, district) 
                dist_num = None
    

            if dist_num:
                person.add_term(role="Member", 
                    org_classification="legislature",
                    label=f"District {dist_num} Councilmember", 
                    district=f"District {dist_num} Councilmember",
                    # NB end_date is REQUIRED. The councilmember querset won't find any council members
                    # if the end dates for their terms aren't set.
                    start_date = CURRENT_TERM_START,
                    end_date = CURRENT_TERM_END)

            else:
                # at large members w/out districts.
                person.add_term(role="Member",
                    org_classification="legislature",
                    label=f"Councilmember at Large",
                    district=f"Councilmember at Large",
                    start_date = CURRENT_TERM_START,
                    end_date = CURRENT_TERM_END)

         
            # TODO sould leadership titles be 'roles', not Posts?
            if re.search("COUNCIL PRESIDENT",subtitle.strip(), re.I):
                # Why do council pres and other leadership roles
                # not get memberships connected so they show up on the list-legislator view?
                person.add_term(
                        role="Council President",
                        org_classification="legislature",
                        label="Council President",
                        # This label-as-district is necessary
                        # because pupa/scrape/popolo.py
                        # needs a way to make a pseudo id
                        # for the Post
                        district="Council President",
                        start_date="2024-01-01",
                        end_date="2025-01-01")
                person.add_name(f"Council President {last_name}")


            if re.search("MAJORITY WHIP", subtitle.strip(), re.I):
                person.add_term(
                        role="Majority Whip",
                        org_classification="legislature",
                        label="Majority Whip",
                        district="Majority Whip",
                        start_date="2024-01-01",
                        end_date="2025-01-01")
                person.add_name(f"Majority Whip {last_name}")


            # TODO Phila site's contact info is a little tedious to parse

            # Add email address.
            #email_xpath = '//a[contains(@href, "mailto")]/@href'
            #email = urls.detail.xpath(email_xpath).pop()[7:]
            #memb.contact_details.append(
            #    dict(type='email', value=email, note='work'))

            # Add sources.
            person.add_source(url)

            # Now we will look at the list of 'extra people'.
            # Some of these are people we'll also find by 
            # scraping, and we need to combine their info.
            # I do this to handle weird spelling issues.
            match, extra_people = find_any_matching_extra_person(person, extra_people)
            if match is not None:
                person = merge_people(match, person)

            yield person


        # if anyody is left in extra_people, yield them too.
        for remaining_person in extra_people:
            yield remaining_person

