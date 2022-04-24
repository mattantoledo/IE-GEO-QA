import requests
import lxml.html

PREFIX = "https://en.wikipedia.org"


def get_countries(url):

    res = requests.get(url)
    doc = lxml.html.fromstring(res.content)

    c1 = doc.xpath("//table[contains(@class, 'wikitable')]/tbody/tr/td[1][not(contains(text(), '('))]/span/a[1]/text()")
    c2 = doc.xpath("//table[contains(@class, 'wikitable')]/tbody/tr/td[1][not(contains(text(), '('))]/a[1]/text()")
    c3 = doc.xpath("//table[contains(@class, 'wikitable')]/tbody/tr/td[1][contains(text(), '(')]/span/a/text()")
    c4 = doc.xpath("//table[contains(@class, 'wikitable')]/tbody/tr/td[1]/i/a[1]/text()")

    countries = c1 + c2 + c3 + c4

    l1 = doc.xpath("//table[contains(@class, 'wikitable')]/tbody/tr/td[1][not(contains(text(), '('))]/span/a[1]/@href")
    l2 = doc.xpath("//table[contains(@class, 'wikitable')]/tbody/tr/td[1][not(contains(text(), '('))]/a[1]/@href")
    l3 = doc.xpath("//table[contains(@class, 'wikitable')]/tbody/tr/td[1][contains(text(), '(')]/span/a/@href")
    l4 = doc.xpath("//table[contains(@class, 'wikitable')]/tbody/tr/td[1]/i/a[1]/@href")

    links = l1 + l2 + l3 + l4

    start = 220
    end = 233

    kk =0

    for i in range(start, end):

        print("Name: " + countries[i])

        res = requests.get(PREFIX + links[i])
        doc = lxml.html.fromstring(res.content)

        infobox = doc.xpath("//table[contains(@class, 'infobox')]")[0]

        try:
            m = infobox.xpath("//table//a[text()='President']")
            president = m[0].xpath("./../../../td/a")
            print("President: " + president[0].text)

            res2 = requests.get(PREFIX + president[0].attrib["href"])
            doc2 = lxml.html.fromstring(res2.content)

            a2 = doc2.xpath("//table[contains(@class, 'infobox')]")
            m2 = a2[0].xpath("//table//th[text()='Born']")
            pob = m2[0].xpath("./../td//a[position()=last()]/text()")
            print("President was born in " + pob[0])

        except Exception:
            print("Fail in President or president place of birth")

        try:
            b = infobox.xpath("//table//a[text()='Prime Minister']")
            prime_minister = b[0].xpath("./../../../td/a")
            print("Prime Minister: " + prime_minister[0].text)

            res2 = requests.get(PREFIX + prime_minister[0].attrib["href"])
            doc2 = lxml.html.fromstring(res2.content)

            a2 = doc2.xpath("//table[contains(@class, 'infobox')]")
            m2 = a2[0].xpath("//table//th[text()='Born']")
            pob = m2[0].xpath("./../td//a[position()=last()]/text()")
            print("Prime Minister was born in " + pob[0])
        except Exception:
            print("Fail in Prime Minister or prime minister place of birth")

        try:
            c = infobox.xpath("//table//a[text()='Population']")

            if c:
                population = c[0].xpath("./../../following-sibling::tr[1]/td/text()")[0]
            else:
                c = infobox[0].xpath("//table//th[text()='Population']")
                population = c[0].xpath("./../following-sibling::tr[1]/td/text()")[0]

            if len(population) < 3:  # russia special case
                population = c[0].xpath("./../../following-sibling::tr[1]/td/div/ul/li[1]/text()")[0]

            print("Population: " + population.strip())
        except Exception:
            print("Fail in Population")

        try:
            d = infobox.xpath("//table//a[text()='Area ' or text()='Area']")

            if d:
                area = d[0].xpath("./../../following-sibling::tr[1]/td/text()")[0]
            else:
                d = infobox[0].xpath("//table//th[text()='Area ' or text()='Area']")
                area = d[0].xpath("./../following-sibling::tr[1]/td/text()")[0]

            print("Area: " + area)
        except Exception:
            print("Fail in Area")

        try:
            e = infobox.xpath("//table//a[text()='Government']")
            if e:
                government_form = e[0].xpath("./../../td//a/@title")
            else:
                e = infobox[0].xpath("//table//th[text()='Government']")
                government_form = e[0].xpath("./../td//a/@title")

            government_form.sort()
            s = ""
            for g in government_form:
                s = s + g + ", "
            print("Government form: "+s[:-2])
        except Exception:
            print("Fail in Government Form")

        try:
            capital = infobox.xpath(".//th[contains(text(), 'Capital') and @class = 'infobox-label']/../td/a/text()")
            if not len(capital):
                capital = infobox.xpath(
                    ".//th[contains(text(), 'Capital') and @class = 'infobox-label']/../td/text()")
            capital = capital[0]
            print("Capital: " + capital)
        except Exception:
            print(countries[i])
            kk += 1
            print("Fail in Capital")

        print("***************")

    print("Done")
    print(kk)


def main():
    url = PREFIX + "/wiki/List_of_countries_by_population_(United_Nations)"

    get_countries(url)


if __name__ == "__main__":
    main()
