from typing import List, Callable, Tuple

from main import *
from template_parser import *


def get_entity_of_relation_query(nl_query: str, parser: Callable[[str], Tuple[Relations, str]]) -> (
        Relations, str, str):
    """
    DONE!
    What is the population of <country>?, Who is the prime minister of <country>?, Who is the president of <country>?"""
    r1, e1 = parser(nl_query)
    if e1 is not None and r1 is not None:
        sparql_query = "SELECT * WHERE { ?e <" + add_ontology_prefix(r1.value) + "> <" + add_ontology_prefix(insert_underscores(e1)) + "> . }"
        return r1, e1, sparql_query
    else:
        raise Exception


def get_elements_in_relation_count_query(nl_query: str, parser: Callable[[str], Tuple[Relations, Relations, str]]) -> (str, Relations, str, str):
    """
    DONE!
    How many presidents/ prime ministers were born in <country>?
    """
    r1, r2, e2 = parser(nl_query)
    if r1 is not None and r2 is not None and e2 is not None:
        sparql_query = "SELECT (COUNT(?person) AS ?count) WHERE {?person <" + add_ontology_prefix(
            r1.value) + "> ?country . ?person <" + add_ontology_prefix(r2.value) + "> <" + add_ontology_prefix(
            e2) + "> . }"
        return r1, r2, e2, sparql_query
    else:
        raise Exception


#TODO: this...
def get_elements_intersection_count_query(nl_query: str,
                                          parser: Callable[[str], Tuple[str, str]]) -> str:
    """How many <government_form1> are also <government_form2>"""
    e1, e2 = parser(nl_query)
    if e1 is not None and e2 is not None:
        return e1, e2, ""
    else:
        raise Exception

#TODO: this..
def get_entity_query(nl_query: str, parser: Callable[[str], str]) -> (str, str):
    """Who is <entity>?"""
    e1 = parser(nl_query)
    if e1 is not None:
        sparql_query = "SELECT ?pms ?presidents WHERE { ?pms <" + add_ontology_prefix(
            Relations.PM_OF.value) + "> ?y . ?presidents <" + add_ontology_prefix(Relations.PRESIDENT_OF.value) + "> ?z   }"
        return e1, sparql_query
    else:
        raise Exception

#TODO: this...
def get_special_substring_query(nl_query: str, parser: Callable[[str], Tuple[str, Relations, str]]) -> (str, Relations, str):
    """List all countries whose capital name contains the string <str>"""
    e1, r1, substring = parser(nl_query)
    if e1 is not None:
        sparql_query = "SELECT * WHERE { ?e <" + add_ontology_prefix(r1.value) + "> <" + add_ontology_prefix(
            insert_underscores(e1)) + "> . }"
        return e1, r1, substring, sparql_query
    else:
        raise Exception

#TODO: this...
def get_entity_of_2_relations(nl_query, parser: Callable[[str], Tuple[Relations, str, Relations]]) -> str:
    """When was the president of <country> born?, where was the prime minister of <country> born?"""
    r1, e1, r2 = parser(nl_query)
    if r1 is not None and e1 is not None and r2 is not None:
        return r1, e1, r2, ""
    else:
        raise Exception


def parse_nl_query_to_structured_query(nl_query: str) -> List[str] or str:
    if nl_query.find(TextStructure.ARE_ALSO.value) != -1:
        return get_elements_intersection_count_query(nl_query, parse_q12_template)

    elif nl_query.find(TextStructure.LIST_ALL.value) != -1:
        return get_special_substring_query(nl_query, parse_q13_template)

    elif nl_query.find(TextStructure.WERE.value) != -1:
        return get_elements_in_relation_count_query(nl_query, parse_q14_template)

    elif nl_query.find(TextStructure.WHO_IS.value) != -1:
        if nl_query.find(TextStructure.WHO_IS_THE.value) != -1:
            return get_entity_of_relation_query(nl_query, parse_who_is_the_template)
        else:
            return get_entity_query(nl_query, parse_q11_template)

    elif nl_query.find(TextStructure.WHAT_IS_THE.value) != -1:
        if nl_query.find(TextStructure.WHAT_IS_THE_FORM_OF.value) != -1:
            return get_entity_of_relation_query(nl_query, parse_what_is_the_form_template)
        else:
            return get_entity_of_relation_query(nl_query, parse_what_is_the_template)

    elif nl_query.find(TextStructure.WHEN_WAS_THE.value) != -1:
        return get_entity_of_2_relations(nl_query, parse_when_was_the_template)

    elif nl_query.find(TextStructure.WHERE_WAS_THE.value) != -1:
        return get_entity_of_2_relations(nl_query, parse_where_was_the_template)

    else:
        return "ERROR"


# TODO: LOWERCASE
# TODO: return None if not found
def main():
    g = rdflib.Graph()
    g.parse('graph.nt', 'nt')
    e1, e2, sparql_query = parse_nl_query_to_structured_query("How many Dogs are also Cats?")
    assert e1 == 'Dogs' and e2 == 'Cats'
    e1, e2, e3, sparql_query = parse_nl_query_to_structured_query(
        "List all countries whose capital name contains the string hi")
    assert e3 == 'hi'
    r1, r2, e3, sparql_query = parse_nl_query_to_structured_query("How many presidents were born in Brazil")
    assert e3 == 'Brazil'
    assert list(g.query(sparql_query))[0][0].value == 1
    r1, r2, e3, sparql_query = parse_nl_query_to_structured_query("How many presidents were born in Iceland")
    assert e3 == 'Iceland'
    print("Presidents born at: " + list(g.query(sparql_query))[0][0].value)

    r, e, sparql_query = parse_nl_query_to_structured_query("Who is the prime minister of Vietnam?")
    assert r == Relations.PM_OF and e == "Vietnam"
    print(list(g.query(sparql_query))[0][0])
    r, e, sparql_query = parse_nl_query_to_structured_query("What is the population of China?")
    assert r == Relations.POPULATION and e == "China"
    print(list(g.query(sparql_query))[0][0])
    r, e, sparql_query = parse_nl_query_to_structured_query("What is the form of government in China?")
    assert r == Relations.POLITICAL_STATUS and e == "China"
    print(list(g.query(sparql_query))[0][0])
    r1, e1, r2, sparql_query = parse_nl_query_to_structured_query("When was the president of Vietnam born?")
    assert r1 == Relations.PRESIDENT_OF and e1 == "Vietnam" and r2 == Relations.DOB
    r1, e1, r2, sparql_query = parse_nl_query_to_structured_query("Where was the prime minister of China born?")
    assert r1 == Relations.PM_OF and e1 == "China" and r2 == Relations.POB
    r1, e1, r2, sparql_query = parse_nl_query_to_structured_query("Where was the prime minister of China born?")
    assert r1 == Relations.PM_OF and e1 == "China" and r2 == Relations.POB
    e1, sparql_query = parse_nl_query_to_structured_query("Who is Phạm Minh Chính?")
    assert e1 == "Phạm Minh Chính"
    # print(sparql_query)
    # print(list(g.query(sparql_query)))
    # print(len(list(g.query(sparql_query))))


if __name__ == "__main__":
    main()
