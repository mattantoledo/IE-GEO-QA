import lxml.html
import requests
import string
import sys
import urllib.parse
from enum import Enum

from rdflib import Literal, XSD, URIRef, Graph

import nl_queries

PREFIX = "https://en.wikipedia.org"
RELATION_PREFIX = "http://example.org/"
COUNTRIES_PATH = "/wiki/List_of_countries_by_population_(United_Nations)"

G = Graph()


class Relations(Enum):
    PRESIDENT_OF = "president_of"
    PM_OF = "prime_minister_of"
    DOB = "born_on"
    POB = "born_at"
    AREA = "area_of"
    POPULATION = "population_of"
    CAPITAL_OF = "capital_of"
    POLITICAL_STATUS = "political_status"


def main(argv):

    if len(argv) < 2:
        print("Not enough arguments")
        return

    if argv[1] == 'create':
        build_ontology(PREFIX + COUNTRIES_PATH)
        G.serialize("ontology.nt", format='nt', encoding='utf-8', errors='ignore')

        print('Finished building')
        return

    elif argv[1] == 'question':

        G.parse(source="ontology.nt", format='nt')
        sparql_query = nl_queries.parse_nl_query_to_structured_query(argv[2])
        results = list(G.query(sparql_query))
        if results:

            results.sort()
            s = ""
            for tup in results:

                a = tup[0]
                b = ''
                p = PREFIX + "/wiki/"

                if type(a) is Literal:
                    if 'area' in argv[2]:
                        a = str(a.value) + ' km squared'
                    else:
                        a = str(a.value)

                elif 'president' in a:
                    a = 'President of '
                elif 'prime' in a:
                    a = 'Prime Minister of '

                elif type(a) is URIRef:
                    a = a[len(p):].replace('_', ' ')
                    a = urllib.parse.unquote(a)

                if len(tup) > 1:
                    b = tup[1]
                    b = b[len(p):].replace('_', ' ')
                    b = urllib.parse.unquote(b)

                s = s + a + b + ', '

            print(s[:-2])
            return

        else:
            print("not found")

    else:
        print("Wrong arguments")
        return


# is_term is True if e2 is number/date (population, area, date of birth)
def insert_into_ontology(e1, relation_property, e2, is_term=False):

    relation_property = RELATION_PREFIX + relation_property.value

    if is_term:
        ent2 = e2
    else:
        ent2 = URIRef(e2)

    x = (URIRef(e1), URIRef(relation_property), ent2)

    G.add(x)


def get_countries(xml_doc):

    a1 = xml_doc.xpath("//table[contains(@class, 'wikitable')]/tbody/tr/td[1][not(contains(text(), '('))]/span/a[1]")
    a2 = xml_doc.xpath("//table[contains(@class, 'wikitable')]/tbody/tr/td[1][not(contains(text(), '('))]/a[1]")
    a3 = xml_doc.xpath("//table[contains(@class, 'wikitable')]/tbody/tr/td[1][contains(text(), '(')]/span/a")
    a4 = xml_doc.xpath("//table[contains(@class, 'wikitable')]/tbody/tr/td[1]/i/a[1]")

    a_list = a1 + a2 + a3 + a4

    countries = [a.attrib["title"] for a in a_list]
    links = [a.attrib["href"] for a in a_list]

    return countries, links


def get_population(infobox) -> string:

    pop_row = infobox.xpath(".//a[text()='Population']/../../following-sibling::tr")

    if not pop_row:
        pop_row = infobox.xpath(".//th[text()='Population']/../following-sibling::tr")

    if pop_row:
        pop_row = pop_row[0]
        pop_list = pop_row.xpath(".//td//text()")
        if pop_list:
            population = pop_list[0]

            # special case for Dominican Republic
            if population == ' ':
                population = pop_list[1]

            # special case for russia case
            if len(population) < 3:
                pop_list = pop_row.xpath(".//td//li/text()")
                if pop_list:
                    population = pop_list[0]

            population = population.split()[0]
            return population
    else:
        return None


def get_area(infobox) -> string:

    area = infobox.xpath(".//a[contains(text(), 'Area')]/../../following-sibling::tr[1]/td/text()")
    if not area:
        area = infobox.xpath(".//th[contains(text(), 'Area')]/../following-sibling::tr[1]/td/text()")

    # special case for Channel Islands
    if not area:
        area = infobox.xpath(".//th[contains(text(), 'Area')]/following-sibling::td[1]/text()")

    if area:
        area = area[0].split()[0]
        return area
    else:
        return None


def get_capital_city(infobox) -> string:

    capital = infobox.xpath(".//th[contains(text(), 'Capital') and @class = 'infobox-label']/../td/a/@href")

    if capital:
        return PREFIX + capital[0]
    else:
        capital = infobox.xpath(".//th[contains(text(), 'Capital') and @class = 'infobox-label']/../td/text()")
        if capital:
            capital = capital[0].rstrip()
            return PREFIX + "/wiki/" + capital.replace(' ', '_')
        else:
            # special case for the capital of Eswatini
            capital = infobox.xpath(".//th[contains(text(), 'Capital') and @class = 'infobox-label']/../td//a[1]/@href")
            if capital:
                return PREFIX + capital[0]
    return None


def get_government_forms(infobox) -> string:

    gov = infobox.xpath(".//a[contains(text(), 'Government')]/../../td//a[not(ancestor::sup)]/@href")
    if not gov:
        gov = infobox.xpath(".//th[contains(text(), 'Government')]/../td//a[not(ancestor::sup)]/@href")

    if gov:
        return [(PREFIX + g) for g in gov]
    else:
        return None


def get_president(infobox) -> string:
    """
    gets president data
    :param infobox: xml
    :return: president url
    """

    president = infobox.xpath(".//a[text()='President']/../../../td/a")

    # special case for Portugal president
    if not president:
        president = infobox.xpath(".//a[text()='President']/../../../td/span/a")

    if president:
        return PREFIX + president[0].attrib["href"]
    else:
        return None


def get_prime_minister(infobox) -> string:
    """
    gets prime minister data
    :param infobox: xml
    :return: pm url
    """

    pm = infobox.xpath(".//a[text()='Prime Minister']/../../../td/a")

    # special case just in case
    if not pm:
        pm = infobox.xpath(".//a[text()='Prime Minister']/../../../td/span/a")

    if pm:
        return PREFIX + pm[0].attrib["href"]
    else:
        return None


def get_place_of_birth(person, countries, links) -> string:

    res = requests.get(person)
    doc = lxml.html.fromstring(res.content)

    infobox = doc.xpath("//table[contains(@class, 'infobox')]")

    if infobox:
        infobox = infobox[0]
        places = infobox.xpath("//table//th[text()='Born']/../td//a[position()=last()][not(ancestor::sup)]/@href")

        # searching birth country as a link
        for place in places:
            if place in links:
                return PREFIX + place

        # searching birth country as text
        places = infobox.xpath("//table//th[text()='Born']/../td//text()")

        values = []
        for p in places:
            values.append(p.strip())
            values.append(p.replace(',', '').strip())
            values.append(p.split())

        for v in values:
            if v in countries:
                country = PREFIX + "/wiki/" + v.replace(' ', '_')
                return country

    return None


def get_date_of_birth(person) -> string:

    res = requests.get(person)
    doc = lxml.html.fromstring(res.content)

    infobox = doc.xpath("//table[contains(@class, 'infobox')]")

    if infobox:
        infobox = infobox[0]
        dob = infobox.xpath("//table//th[text()='Born']/../td//span[@class='bday']/text()")
        if dob:
            return dob[0]

    return None


def insert_underscores(item: string):
    return item.replace(" ", "_")


def build_ontology(url):
    res = requests.get(url)
    doc = lxml.html.fromstring(res.content)

    countries, links = get_countries(doc)

    start = 0
    end = len(countries)

    for i in range(start, end):

        res = requests.get(PREFIX + links[i])
        doc = lxml.html.fromstring(res.content)

        country = PREFIX + links[i]

        infobox = doc.xpath("//table[contains(@class, 'infobox')]")[0]

        president = get_president(infobox)

        if president:
            insert_into_ontology(country, Relations.PRESIDENT_OF, president)

            pob = get_place_of_birth(president, countries, links)
            if pob:
                insert_into_ontology(president, Relations.POB, pob)

            dob = get_date_of_birth(president)
            if dob:
                insert_into_ontology(president, Relations.DOB, Literal(dob), is_term=True)

        prime_minister = get_prime_minister(infobox)

        if prime_minister:
            insert_into_ontology(country, Relations.PM_OF, prime_minister)

            pob = get_place_of_birth(prime_minister, countries, links)
            if pob:
                insert_into_ontology(prime_minister, Relations.POB, pob)

            dob = get_date_of_birth(prime_minister)
            if dob:
                insert_into_ontology(prime_minister, Relations.DOB, Literal(dob, datatype=XSD.date), is_term=True)

        country_population = get_population(infobox)
        if country_population:
            insert_into_ontology(country, Relations.POPULATION, Literal(country_population), is_term=True)

        country_area = get_area(infobox)
        if country_area:
            insert_into_ontology(country, Relations.AREA, Literal(country_area), is_term=True)

        government_forms = get_government_forms(infobox)

        if government_forms:
            for form in government_forms:
                insert_into_ontology(country, Relations.POLITICAL_STATUS, form)

        capital_city = get_capital_city(infobox)
        if capital_city:
            insert_into_ontology(country, Relations.CAPITAL_OF, capital_city)


if __name__ == "__main__":
    main(sys.argv)
