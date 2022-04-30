import sys

import lxml.html

from nl_queries import *

PREFIX = "https://en.wikipedia.org"
ONTOLOGY_PREFIX = "http://example.org/"
COUNTRIES_PATH = "/wiki/List_of_countries_by_population_(United_Nations)"

G = rdflib.Graph()


def main(argv):

    if len(argv) < 2:
        print("Not enough arguments")
        return

    if argv[1] == 'create':
        build_ontology(PREFIX + COUNTRIES_PATH)
        G.serialize("ontology.nt", format='nt')
        print('Finished building')
        return

    elif argv[1] == 'question':
        sparql_query = parse_nl_query_to_structured_query(argv[2])[-1]
        print_result(G, sparql_query)

    else:
        print("Wrong arguments")
        return


def insert_into_ontology(e1, relation_property, e2):
    if e1 is None:
        e1 = "None"
    if e2 is None:
        e2 = "None"
    e1 = add_ontology_prefix(insert_underscores(e1))
    relation_property = add_ontology_prefix(relation_property.value)
    e2 = add_ontology_prefix(insert_underscores(e2))
    G.add((rdflib.URIRef(e1), rdflib.URIRef(relation_property), rdflib.URIRef(e2)))


def build_ontology(url):
    res = requests.get(url)
    doc = lxml.html.fromstring(res.content)

    countries = get_countries(doc)
    links = get_links(doc)

    start = 0
    end = len(countries)

    for i in range(start, end):
        country = countries[i]

        res = requests.get(PREFIX + links[i])
        doc = lxml.html.fromstring(res.content)

        infobox = doc.xpath("//table[contains(@class, 'infobox')]")[0]

        president_name, president_pob, president_dob = get_president_data(infobox)
        insert_into_ontology(president_name, Relations.PRESIDENT_OF, country)
        insert_into_ontology(president_name, Relations.POB, president_pob)
        insert_into_ontology(president_name, Relations.DOB, president_dob)

        pm_name, pm_pob, pm_dob = get_prime_minister_data(infobox)
        insert_into_ontology(pm_name, Relations.PM_OF, country)
        insert_into_ontology(pm_name, Relations.POB, pm_pob)
        insert_into_ontology(pm_name, Relations.DOB, pm_dob)

        country_population = get_population_data(infobox)
        insert_into_ontology(country_population, Relations.POPULATION, country)

        country_area = get_geographic_data(infobox)
        insert_into_ontology(country_area, Relations.AREA, country)

        political_data = get_political_data(infobox)
        insert_into_ontology(political_data, Relations.POLITICAL_STATUS, country)

        capital_city = get_capital_city_data(infobox)
        insert_into_ontology(capital_city, Relations.CAPITAL_OF, country)


if __name__ == "__main__":
    main(sys.argv)
