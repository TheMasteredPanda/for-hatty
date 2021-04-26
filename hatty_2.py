import asyncio
from enum import Enum
import random
import string
from PIL import ImageDraw, Image, ImageFont
from ukparliament.ukparliament import UKParliament
from ukparliament.structures.bills import LordsDivision, CommonsDivision
from ukparliament.structures.members import PartyMember, Party
from typing import Union
import math


class PartyColour(Enum):
    ALBA = {"id": 1034, "colour": '#73BFFA'}
    ALLIANCE = {"id": 1, "colour": '#D5D5D5'}
    CONSERVATIVE = {"id": 4, "colour": '#489FF8'}
    DUP = {"id": 7, "colour": '#3274B5'}
    GREEN = {"id": 44, "colour": '#82D552'}
    INDEPENDENT = {"id": 8, "colour": '#929292'}
    LABOUR = {"id": 15, "colour": '#DB3B26'}
    LIBERAL = {"id": 17, "colour": '#F19937'}
    PLAID_CYMRU = {"id": 22, "colour": '#54AE33'}
    SNP = {"id": 29, "colour": '#EFBD40'}
    SINN_FEIN = {"id": 30, "colour": '#986541'}
    SDLP = {"id": 31, "colour": '#ED6D57'}
    BISHOPS = {"id": 3, "colour": '#8648BA'}
    CONSERVATIVE_IND = {"id": 5, 'colour': "#ED6D57"}
    CROSSBENCH = {"id": 6, 'colour': "#A99166"}
    IND_SOCIAL_DEMOCRATS = {"id": 53, 'colour': '#A62A16'}
    LABOUR_IND = {"id": 43, 'colour': '#DE68A5'}
    ULSTER_UNIONIST = {"id": 38, 'colour': '#8648BA'}
    NONAFFILIATED = {"id": 49, 'colour': '#929292'}

    @classmethod
    def from_id(cls, value: int):
        for p_enum in cls:
            if p_enum.value['id'] == value:
                return p_enum
        return cls.NONAFFILIATED

title_font = ImageFont.truetype('Metropolis-Bold.otf', 40)
key_font = ImageFont.truetype('Metropolis-SemiBold.otf', 25)

def generate_division_image(parliament: UKParliament, division: Union[LordsDivision, CommonsDivision]):
    def draw_ayes(draw: ImageDraw.ImageDraw, members: list[PartyMember]):
        columns = math.ceil(len(members) / 10)
        draw.text((100, 420), "Ayes", font=title_font, fill=(0,0,0))

        for column in range(columns + 1):
            for j, member in enumerate(members[10 * (column - 1): 10 * column]):
                draw.ellipse([(80 + ((20 * column) + (2 * column)), 480 + (20 * j) + (2 * j)), (100 + ((20 * column) + (2 * column)), 500 + (20 * j) + (2 * j) - 2)], f"{PartyColour.from_id(member._get_party_id()).value['colour']}")

    def draw_noes(draw: ImageDraw.ImageDraw, members: list[PartyMember]):
        columns = math.ceil(len(members) / 10)
        draw.text((100, 120), "Noes", font=title_font, fill=(0,0,0))
        for column in range(columns + 1):
            for j, member in enumerate(members[10 * (column - 1): 10 * column]):
                party = parliament.get_party_by_id(member._get_party_id())
                draw.ellipse([(80 + ((20 * column) + (2 * column)), 180 + (20 * j) + (2 * j)), (100 + ((20 * column) + ((2 * column) - 2)), 200 + (20 * j) + ((2 * j) - 2))], f"{PartyColour.from_id(member._get_party_id()).value['colour']}")


    def get_parties(division: Union[CommonsDivision, LordsDivision]) -> list[Party]:
        party_ids = []

        for member in division.get_aye_members():
            party_id = member._get_party_id()
            if party_id not in party_ids:
                party_ids.append(party_id)

        for member in division.get_no_members():
            party_id = member._get_party_id()
            if party_id not in party_ids:
                party_ids.append(party_id)

        return list(filter(lambda party: party is not None, map(lambda p_id: parliament.get_party_by_id(p_id), party_ids))) # type: ignore

    def draw_keys(draw: ImageDraw.ImageDraw, division: Union[CommonsDivision, LordsDivision]):
        parties = get_parties(division)

        for i, party in enumerate(parties):
            name = party.get_name()
            w, h = draw.textsize(name)
            draw.text((1600, 120 + (60 * i)), f"{name}", font=key_font, fill='#ffffff', anchor='lt')
            draw.ellipse([(1520, 110 + (60 * i)), (1570, 150 + (60 * i))], fill=f"{PartyColour.from_id(party.get_party_id()).value['colour']}")

    def sort_members(members: list[PartyMember]) -> list[PartyMember]:
        parties = {}

        for member in members:
            if member._get_party_id() not in parties:
                parties[member._get_party_id()] = [member]
            else:
                parties[member._get_party_id()].append(member)

        results = []

        for key in sorted(parties.keys(), key=lambda k: len(parties[k])):
            results.extend(parties[key])
        
        results.reverse()
        return results

    im = Image.new('RGB', (2100, 800), '#edebea')
    draw = ImageDraw.Draw(im)
    draw.rectangle([(1450, 0), (2100, 800)], fill='#b7dade')
    draw.polygon([(1300, 0), (1450, 0), (1450, 800)], fill='#b7dade')
    draw_ayes(draw, sort_members(division.get_aye_members()))
    draw_noes(draw, sort_members(division.get_no_members()))
    draw_keys(draw, division)
    file_id = ''.join(random.choice(string.ascii_lowercase) for i in range(20))
    im.save(f"{file_id}.png", "PNG")


parliament = UKParliament()
asyncio.run(parliament.load())
divisions = asyncio.run(parliament.search_for_commons_divisions(result_limit=1))
division = divisions[0]
n_division = asyncio.run(parliament.get_commons_division(division.get_id()))
generate_division_image(parliament, n_division)
