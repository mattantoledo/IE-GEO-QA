from enum import Enum

from main import Relations


# TODO: Is the Ok?
# TODO: what happens if a query looks like this - who was the born at vietnam?
class TextStructure(Enum):
    ARE_ALSO = " are also "  # Question 12

    LIST_ALL = "List all "  # Question 13

    WERE = " were "  # Question 14

    WHO_IS = "Who is "  # Question 11
    WHO_IS_THE = "Who is the "  # Questions 1,2

    WHAT_IS_THE = "What is the "  # Questions 3,4,6
    WHAT_IS_THE_FORM_OF = "What is the form of "  # Question 5

    WHEN_WAS_THE = "When was the "  # Questions 7,9

    WHERE_WAS_THE = "Where was the "  # Questions 8,10


def parse_who_is_the_template(nl_query: str) -> (Relations, str):
    cleaned_nl_query = nl_query.replace(" ", "_")
    for r in Relations:
        if cleaned_nl_query.find(r.value) != -1:
            return r, cleaned_nl_query[len("Who is the ") + len(r.value) + 1:-1]
    return None, None


def parse_what_is_the_template(nl_query: str) -> (Relations, str):
    cleaned_nl_query = nl_query.replace(" ", "_")
    for r in Relations:
        if cleaned_nl_query.find(r.value) != -1:
            return r, cleaned_nl_query[len("What is the ") + len(r.value) + 1:-1]
    return None, None


def parse_what_is_the_form_template(nl_query: str) -> (Relations, str):
    return Relations.POLITICAL_STATUS, nl_query[len("What is the form of government in "):-1]


def parse_when_was_the_template(nl_query: str) -> (Relations, str, Relations):
    cleaned_nl_query = nl_query.replace(" ", "_")
    for r in Relations:
        if cleaned_nl_query.find(r.value) != -1:
            return r, cleaned_nl_query[len("When was the ") + len(r.value) + 1:-6], Relations.DOB
    return None, None, None


def parse_where_was_the_template(nl_query: str) -> (Relations, str, Relations):
    cleaned_nl_query = nl_query.replace(" ", "_")
    for r in Relations:
        if cleaned_nl_query.find(r.value) != -1:
            return r, cleaned_nl_query[len("Where was the ") + len(r.value) + 1:-6], Relations.POB
    return None, None


def parse_q11_template(nl_query: str) -> str:
    substring_idx = len("Who is ")
    e1 = nl_query[substring_idx:-1]
    return e1


def parse_q12_template(nl_query: str) -> (str, str):
    are_also_idx = nl_query.find(TextStructure.ARE_ALSO.value)
    e1 = nl_query[9:are_also_idx]
    e2 = nl_query[are_also_idx + 10:-1]
    return e1, e2


def parse_q13_template(nl_query: str) -> (str, Relations, str):  # TODO: Is this ok ? Only one arg....
    substring_idx = len("List all countries whose capital name contains the string ")
    substring = nl_query[substring_idx:]
    return "countries", Relations.CAPITAL_OF, substring


def parse_q14_template(nl_query: str) -> (str, Relations, str):  # TODO: is this ok? or do we need PMs as well
    substring_idx = len("How many presidents were born in ")
    e2 = nl_query[substring_idx:]
    return Relations.PRESIDENT_OF, Relations.POB, e2


def main():
    e1, e2 = parse_q12_template("How many Dogs are also Cats?")
    assert e1 == 'Dogs' and e2 == 'Cats'
    e1, e2, e3 = parse_q13_template("List all countries whose capital name contains the string hi")
    assert e3 == 'hi'
    e1, e2, e3 = parse_q14_template("How many presidents were born in Colorado")
    assert e3 == 'Colorado'
    r, e = parse_who_is_the_template("Who is the prime minister of Vietnam?")
    assert r == Relations.PM_OF and e == "Vietnam"
    r, e = parse_what_is_the_template("What is the population of China?")
    assert r == Relations.POPULATION and e == "China"
    r, e = parse_what_is_the_template("What is the population of China?")
    assert r == Relations.POPULATION and e == "China"
    r, e = parse_what_is_the_form_template("What is the form of government in China?")
    assert r == Relations.POLITICAL_STATUS and e == "China"
    r, e = parse_what_is_the_form_template("What is the form of government in China?")
    assert r == Relations.POLITICAL_STATUS and e == "China"
    r1, e1, r2 = parse_when_was_the_template("When was the president of Vietnam born?")
    assert r1 == Relations.PRESIDENT_OF and e1 == "Vietnam" and r2 == Relations.DOB
    r1, e1, r2 = parse_where_was_the_template("Where was the prime minister of China born?")
    assert r1 == Relations.PM_OF and e1 == "China" and r2 == Relations.POB


if __name__ == "__main__":
    main()
