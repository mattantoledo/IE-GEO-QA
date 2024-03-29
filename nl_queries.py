from typing import List, Callable, Tuple

from template_parser import *
from geo_qa import insert_underscores

PREFIX = "https://en.wikipedia.org/wiki/"
RELATION_PREFIX = "http://example.org/"


def get_entity_of_relation_query(nl_query: str, parser: Callable[[str], Tuple[Relations, str]]) -> str:
    """
    DONE!
    What is the population of <country>?, Who is the prime minister of <country>?, Who is the president of <country>?"""
    r1, e1 = parser(nl_query)

    # TODO maybe need to do this for all queries
    # special case for Saint Helena, Ascension and Tristan da Cunha
    if ',' in e1:
        sparql_query = "PREFIX rel:<" + RELATION_PREFIX + "> " \
                                                          "SELECT ?data WHERE { <" + PREFIX + insert_underscores(
            e1) + "> rel:" + r1.value + " ?data . }"
        return sparql_query

    if e1 is not None and r1 is not None:
        sparql_query = "PREFIX ent:<" + PREFIX + "> " \
                                                 "PREFIX rel:<" + RELATION_PREFIX + "> " \
                                                                                    "SELECT ?data WHERE { ent:" + insert_underscores(
            e1) + " rel:" + r1.value + " ?data . }"
        return sparql_query
    else:
        raise Exception


def get_elements_in_relation_count_query(nl_query: str, parser: Callable[[str], Tuple[Relations, Relations, str]]) -> str:
    """
    DONE!
    How many presidents were born in <country>?
    """
    r1, r2, e2 = parser(nl_query)
    if r1 is not None and r2 is not None and e2 is not None:
        sparql_query = "PREFIX ent: <" + PREFIX + ">" \
                                                  "PREFIX rel:<" + RELATION_PREFIX + "> " \
                                                                                     "SELECT (COUNT(?person) AS ?num) " \
                                                                                     "WHERE { ?country rel:" + r1.value + " ?person ." \
                                                                                                                          " ?person rel:" + r2.value + " ent:" + insert_underscores(
            e2) + " }"
        return sparql_query
    else:
        raise Exception


# TODO: change ontologies so that each form is by itself (not a list)
def get_elements_intersection_count_query(nl_query: str,
                                          parser: Callable[[str], Tuple[str, str]]) -> str:
    """How many <government_form1> are also <government_form2>"""
    e1, e2 = parser(nl_query)

    form1 = insert_underscores(e1)
    form2 = insert_underscores(e2)
    r = Relations.POLITICAL_STATUS.value

    if e1 is not None and e2 is not None:

        sparql_query = "PREFIX ent: <" + PREFIX + ">" \
                                                  "PREFIX rel:<" + RELATION_PREFIX + "> " \
                                                                                     "SELECT (COUNT(?country) AS ?num) WHERE { ?country rel:" + r + " ent:" + form1 + " . " \
                                                                                                                                                                      "?country rel:" + r + " ent:" + form2 + " }"

        return sparql_query
    else:
        raise Exception


def get_entity_query(nl_query: str, parser: Callable[[str], str]) -> str:
    """Who is <entity>?"""

    e1 = parser(nl_query)

    person = insert_underscores(e1)
    pr_of = Relations.PRESIDENT_OF.value
    pm_of = Relations.PM_OF.value

    if e1 is not None:
        sparql_query = "PREFIX ent:<" + PREFIX + ">" \
                                                 "PREFIX rel:<" + RELATION_PREFIX + "> " \
                                                                                    "SELECT ?job ?country " \
                                                                                    "WHERE {" \
                                                                                    "?country ?job ent:" + person + " ." \
                                                                                                                    " FILTER( ?job = rel:" + pm_of + " || ?job = rel:" + pr_of + ")" \
                                                                                                                                                                                 " }"

        return sparql_query
    else:
        raise Exception


def get_special_substring_query(nl_query: str, parser: Callable[[str], Tuple[str, Relations, str]]) -> str:
    """
    List all countries whose capital name contains the string <str>
    Case insensitive
    """

    e1, r1, substring = parser(nl_query)
    if e1 is not None:

        sparql_query = "PREFIX ent:<" + PREFIX + ">" \
                                                 "PREFIX rel:<" + RELATION_PREFIX + "> " \
                                                                                    "SELECT ?country " \
                                                                                    "WHERE { ?country rel:" + r1.value + " ?city ." \
                                                                                                                         " FILTER( CONTAINS(lcase(str(?city)), '" + substring + "')) }"

        return sparql_query
    else:
        raise Exception


def get_entity_of_2_relations(nl_query, parser: Callable[[str], Tuple[Relations, str, Relations]]) -> str:
    """When was the president of <country> born?, where was the prime minister of <country> born?"""
    r1, e1, r2 = parser(nl_query)

    country = insert_underscores(e1)
    if r1 is not None and e1 is not None and r2 is not None:

        sparql_query = "PREFIX ent: <" + PREFIX + ">" \
                                                  "PREFIX rel:<" + RELATION_PREFIX + "> " \
                                                                                     "SELECT ?data WHERE { ent:" + country + " rel:" + r1.value + " ?person . " \
                                                                                                                                                  "?person rel:" + r2.value + "  ?data }"

        return sparql_query
    else:
        raise Exception


def get_custom_query(nl_query, parser: Callable[[str], Tuple[Relations, str]]) -> str:
    r, dob_string = parser(nl_query)

    sparql_query = "PREFIX ent:<" + PREFIX + ">" \
                                             "PREFIX rel:<" + RELATION_PREFIX + "> " \
                                                                                "SELECT ?person " \
                                                                                "WHERE { ?person rel:" + r.value + " ?dob ." \
                                                                                                                   " FILTER( CONTAINS(lcase(str(?dob)), '" + dob_string + "')) }"
    return sparql_query


def parse_nl_query_to_structured_query(nl_query: str) -> List[str] or str:

    nl_query = ' '.join(nl_query.split())

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

    elif nl_query.find(TextStructure.BORN_ON.value) != -1:
        return get_custom_query(nl_query, parse_who_was_born_on_template)

    else:
        return "ERROR"
