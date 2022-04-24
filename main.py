import string
from enum import Enum

import lxml.html
import rdflib
import requests

PREFIX = "https://en.wikipedia.org"
G = rdflib.Graph()
ONTOLOGY_PREFIX = "http://example.org/"


class Relations(Enum):
    PRESIDENT_OF = "president_of"
    PM_OF = "prime_minister_of"
    DOB = "born_on"
    POB = "born_at"
    AREA = "area_of"
    POPULATION = "population_of"
    CAPITAL_OF = "capital_of"
    POLITICAL_STATUS = "political_status"


def get_countries(xml_doc):

    c1 = xml_doc.xpath("//table[contains(@class, 'wikitable')]/tbody/tr/td[1][not(contains(text(), '('))]/span/a[1]/text()")
    c2 = xml_doc.xpath("//table[contains(@class, 'wikitable')]/tbody/tr/td[1][not(contains(text(), '('))]/a[1]/text()")
    c3 = xml_doc.xpath("//table[contains(@class, 'wikitable')]/tbody/tr/td[1][contains(text(), '(')]/span/a/text()")
    c4 = xml_doc.xpath("//table[contains(@class, 'wikitable')]/tbody/tr/td[1]/i/a[1]/text()")
    return c1 + c2 + c3 + c4


def get_links(xml_doc):
    l1 = xml_doc.xpath("//table[contains(@class, 'wikitable')]/tbody/tr/td[1][not(contains(text(), '('))]/span/a[1]/@href")
    l2 = xml_doc.xpath("//table[contains(@class, 'wikitable')]/tbody/tr/td[1][not(contains(text(), '('))]/a[1]/@href")
    l3 = xml_doc.xpath("//table[contains(@class, 'wikitable')]/tbody/tr/td[1][contains(text(), '(')]/span/a/@href")
    l4 = xml_doc.xpath("//table[contains(@class, 'wikitable')]/tbody/tr/td[1]/i/a[1]/@href")
    return l1 + l2 + l3 + l4


def get_president_data(infobox) -> [string, string]:
    """
    gets president data
    :param a: xml
    :return: president name, place of birth
    """

    president = infobox.xpath(".//a[text()='President']/../../../td/a")
    if len(president):
        president = president[0]
        print("President: " + president.text)

        res2 = requests.get(PREFIX + president.attrib["href"])
        doc2 = lxml.html.fromstring(res2.content)

        infobox2 = doc2.xpath("//table[contains(@class, 'infobox')]")[0]
        pob = infobox2.xpath("//table//th[text()='Born']/../td//a[position()=last()]/text()")

        if len(pob):
            pob = pob[0]
            print("President was born in " + pob)
            return president.text, pob
        else:
            print("Fail in president place of birth")
            return president.text, None
    else:
        print("Fail in President")
        return None, None


def get_prime_minister_data(infobox) -> [string, string]:
    """
    gets prime minister data
    :param a: xml
    :return: prime minister name, place of birth
    """
    prime_minister = infobox.xpath(".//a[text()='Prime Minister']/../../../td/a")
    if len(prime_minister):
        prime_minister = prime_minister[0]
        print("Prime Minister: " + prime_minister.text)

        res2 = requests.get(PREFIX + prime_minister.attrib["href"])
        doc2 = lxml.html.fromstring(res2.content)

        infobox2 = doc2.xpath("//table[contains(@class, 'infobox')]")[0]
        pob = infobox2.xpath("//table//th[text()='Born']/../td//a[position()=last()]/text()")

        if len(pob):
            pob = pob[0]
            print("Prime Minister was born in " + pob)
            return prime_minister.text, pob
        else:
            print("Fail in Prime Minister place of birth")
            return prime_minister.text, None
    else:
        print("Fail in Prime Minister")
        return None, None


def get_population_data(infobox) -> string:

    population = infobox.xpath(".//a[text()='Population']/../../following-sibling::tr[1]/td/text()")
    if not len(population):
        population = infobox.xpath(".//th[text()='Population']/../following-sibling::tr[1]/td/text()")

    if len(population):
        population = population[0].strip()
        if len(population) < 3:  # russia special case
            population = infobox.xpath(".//a[text()='Population']/../../following-sibling::tr[1]/td/div/ul/li[1]/text()")[0]
        print("Population: " + population)
        return population
    else:
        print("Fail in Population")
        return None


def get_geographic_data(infobox) -> string:

    area = infobox.xpath(".//a[contains(text(), 'Area')]/../../following-sibling::tr[1]/td/text()")
    if not len(area):
        area = infobox.xpath(".//th[contains(text(), 'Area')]/../following-sibling::tr[1]/td/text()")

    if len(area):
        area = area[0].split()[0] + " km squared"
        print("Area: " + area)
        return area
    else:
        print("Fail in Area")
        return None


def get_political_data(infobox) -> string:

    gov = infobox.xpath(".//a[contains(text(), 'Government')]/../../td//a/@title")
    if not len(gov):
        gov = infobox.xpath(".//th[contains(text(), 'Government')]/../td//a/@title")

    if len(gov):
        gov.sort()
        gov_str = ""
        for g in gov:
            gov_str = gov_str + g + ", "
        print("Government form: " + gov_str[:-2])
        return gov_str[:-2]
    else:
        print("Fail in Government Form")
        return None


def get_capital_city_data(infobox) -> string:

    capital = infobox.xpath(".//th[contains(text(), 'Capital') and @class = 'infobox-label']/../td/a/text()")

    if not len(capital):
        capital = infobox.xpath(".//th[contains(text(), 'Capital') and @class = 'infobox-label']/../td/text()")

    if len(capital):
        capital = capital[0]
        print("Capital: " + capital)
        return capital
    else:
        print("Fail in Capital")
        return None


def add_ontology_prefix(item: string):
    return (f"{ONTOLOGY_PREFIX}{item}")


def insert_underscores(item: string):
    return item.replace(" ", "_")


def insert_into_ontology(e1, relation_property, e2):
    if e1 is None:
        e1 = "None"
    if e2 is None:
        e2 = "None"
    e1 = add_ontology_prefix(insert_underscores(e1))
    relation_property = add_ontology_prefix(relation_property)
    e2 = add_ontology_prefix(insert_underscores(e2))
    G.add((rdflib.URIRef(e1), rdflib.URIRef(relation_property), rdflib.URIRef(e2)))


def get_data(url):
    res = requests.get(url)
    doc = lxml.html.fromstring(res.content)

    countries = get_countries(doc)
    links = get_links(doc)

    start = 0
    end = 50
    # g.parse('graph.nt', 'nt')
    for i in range(start, end):
        country = countries[i]
        print("Name: " + country)

        res = requests.get(PREFIX + links[i])
        doc = lxml.html.fromstring(res.content)

        infobox = doc.xpath("//table[contains(@class, 'infobox')]")[0]

        president_name, president_pob = get_president_data(infobox)
        insert_into_ontology(president_name, Relations.PRESIDENT_OF, country)
        insert_into_ontology(president_pob, Relations.POB, country)

        pm_name, pm_pob = get_prime_minister_data(infobox)
        insert_into_ontology(pm_name, Relations.PM_OF, country)
        insert_into_ontology(pm_pob, Relations.POB, country)

        country_population = get_population_data(infobox)
        insert_into_ontology(country_population, Relations.POPULATION, country)

        country_area = get_geographic_data(infobox)
        insert_into_ontology(country_area, Relations.AREA, country)

        political_data = get_political_data(infobox)
        insert_into_ontology(political_data, Relations.POLITICAL_STATUS, country)

        capital_city = get_capital_city_data(infobox)
        insert_into_ontology(capital_city, Relations.CAPITAL_OF, country)

        print("***************")
    #G.serialize('graph.nt', 'nt')
    print("Done")


def main():
    url = PREFIX + "/wiki/List_of_countries_by_population_(United_Nations)"

    get_data(url)


if __name__ == "__main__":
    main()
