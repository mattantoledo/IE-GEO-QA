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
    return xml_doc.xpath("//table[contains(@class, 'wikitable')]/tbody/tr/td[1]/span/a/text()")


def get_links(xml_doc):
    return xml_doc.xpath("//table[contains(@class, 'wikitable')]/tbody/tr/td[1]/span/a/@href")


def get_president_data(a) -> [string, string]:
    """
    gets president data
    :param a: xml
    :return: president name, place of birth
    """
    try:
        m = a[0].xpath("//table//a[text()='President']")
        president = m[0].xpath("./../../../td/a")
        print("President: " + president[0].text)

        res2 = requests.get(PREFIX + president[0].attrib["href"])
        doc2 = lxml.html.fromstring(res2.content)

        a2 = doc2.xpath("//table[contains(@class, 'infobox')]")
        m2 = a2[0].xpath("//table//th[text()='Born']")
        pob = m2[0].xpath("./../td//a[position()=last()]/text()")
        print("President was born in " + pob[0])
        return president[0].text, pob[0]
    except Exception:
        print("Fail in President or president place of birth")
        return None, None


def get_prime_minister_data(a) -> [string, string]:
    """
    gets prime minister data
    :param a: xml
    :return: prime minister name, place of birth
    """
    try:
        b = a[0].xpath("//table//a[text()='Prime Minister']")
        prime_minister = b[0].xpath("./../../../td/a")
        print("Prime Minister: " + prime_minister[0].text)

        res2 = requests.get(PREFIX + prime_minister[0].attrib["href"])
        doc2 = lxml.html.fromstring(res2.content)

        a2 = doc2.xpath("//table[contains(@class, 'infobox')]")
        m2 = a2[0].xpath("//table//th[text()='Born']")
        pob = m2[0].xpath("./../td//a[position()=last()]/text()")
        print("Prime Minister was born in " + pob[0])
        return prime_minister[0].text, pob[0]

    except Exception:
        print("Fail in Prime Minister or prime minister place of birth")
        return None, None


def get_population_data(a) -> string:
    try:
        c = a[0].xpath("//table//a[text()='Population']")

        if c:
            population = c[0].xpath("./../../following-sibling::tr[1]/td/text()")[0]
        else:
            c = a[0].xpath("//table//th[text()='Population']")
            population = c[0].xpath("./../following-sibling::tr[1]/td/text()")[0]
        print("Population: " + population.strip())
        return population.strip()
    except Exception:
        print("Fail in Population")
        return None


def get_geographic_data(a) -> string:
    try:
        d = a[0].xpath("//table//a[text()='Area ' or text()='Area']")

        if d:
            area = d[0].xpath("./../../following-sibling::tr[1]/td/text()")[0]
        else:
            d = a[0].xpath("//table//th[text()='Area ' or text()='Area']")
            area = d[0].xpath("./../following-sibling::tr[1]/td/text()")[0]

        print("Area: " + area)
        return area

    except Exception:
        print("Fail in Area")
        return None


def get_political_data(a) -> string:
    try:
        e = a[0].xpath("//table//a[text()='Government']")
        if e:
            government_form = e[0].xpath("./../../td//a/@title")
        else:
            e = a[0].xpath("//table//th[text()='Government']")
            government_form = e[0].xpath("./../td//a/@title")

        government_form.sort()
        s = ""
        for g in government_form:
            s = s + g + ", "
        print("Government form: " + s[:-2])
        return s[:-2]
    except Exception:
        print("Fail in Government Form")
        return None


def get_capital_city_data(a) -> string:
    try:
        f = a[0].xpath("//table//th[text() = 'Capital' and @class = 'infobox-label']")
        capital = f[0].xpath("./../td/a/text()")[0]
        print("Capital: " + capital)
        return capital
    except Exception:
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

    start = 1
    end = 20
    # g.parse('graph.nt', 'nt')
    for i in range(start, end):
        country = countries[i]
        print("Name: " + country)

        res = requests.get(PREFIX + links[i])
        doc = lxml.html.fromstring(res.content)

        a = doc.xpath("//table[contains(@class, 'infobox')]")

        president_name, president_pob = get_president_data(a)
        insert_into_ontology(president_name, Relations.PRESIDENT_OF, country)
        insert_into_ontology(president_pob, Relations.POB, country)

        pm_name, pm_pob = get_prime_minister_data(a)
        insert_into_ontology(pm_name, Relations.PM_OF, country)
        insert_into_ontology(pm_pob, Relations.POB, country)

        country_population = get_population_data(a)
        insert_into_ontology(country_population, Relations.POPULATION, country)

        country_area = get_geographic_data(a)
        insert_into_ontology(country_area, Relations.AREA, country)

        political_data = get_political_data(a)
        insert_into_ontology(political_data, Relations.POLITICAL_STATUS, country)

        capital_city = get_capital_city_data(a)
        insert_into_ontology(capital_city, Relations.CAPITAL_OF, country)

        print("***************")
    G.serialize('graph.nt', 'nt')
    print("Done")


def main():
    url = PREFIX + "/wiki/List_of_countries_by_population_(United_Nations)"

    get_data(url)


if __name__ == "__main__":
    main()
