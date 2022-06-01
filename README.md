## Geographical Q&A

In [geo_qa.py](https://github.com/mattantoledo/WebInformationExtractor/blob/main/geo_qa.py) I implemented a web crawler, that extracts information about all existing countries in the world from [Wikipedia](https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)).

Using XPATH, we extract the following input from each country's wiki page:
* Population
* Capital
* Area
* Government 
* President
* Prime Minister
* Form of Government
* For each Prime minister or President, we also extract their date of birth and place of birth.

The mentioned info is stored as relations in an ontology, created using rdflib.
You can see the ontology itself in [ontology.nt](https://github.com/mattantoledo/WebInformationExtractor/blob/main/ontology.nt).

The ontology can be queried using SPARQL.
In addition you can query the ontology by natural language, using the following question structures:
1. Who is the **president** of *country*?
2. Who is the **prime minister** of *country*?
3. What is the **population** of *country*?
4. What is the **area** of *country*?
5. What is the **form of government** of *country*?
6. What is the **capital** of *country*?
7. When was the **president** of *country*?
8. Where was the **president** of *country*?
9. When was the **prime minister** of *country* born?
10. Where was the **prime minister** of *country* born?
11. Who is *person*?
12. How many **government_form1** are also **government_form2**?
13. List all countries whose capital name contains the string **str**
14. How many presidents were born in *country*?
15. Who was born on **date**?  

### Code Structure

* [geo_qa.py][1] is the main file for creating the ontology and querying it.
* [template_parser.py][2] extracts the entities and relations in the question, based on the 15 question templates from above.
* [nl_queries.py][3] parses the natural language question to a SPARQL query, using [template_parser.py][2]

[1]: https://github.com/mattantoledo/WebInformationExtractor/blob/main/geo_qa.py
[2]: https://github.com/mattantoledo/WebInformationExtractor/blob/main/template_parser.py
[3]: https://github.com/mattantoledo/WebInformationExtractor/blob/main/nl_queries.py

### Run Instructions ###

To create the ontology, run from the cmd line:<br>
```python geo_qa.py create```<br>
To query an existing ontology, run:<br>
```python geo_qa.py question "What is the population of China?"``` 
