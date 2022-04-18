import requests
import lxml.html

PREFIX = "https://en.wikipedia.org"


def get_countries(url):

    res = requests.get(url)
    doc = lxml.html.fromstring(res.content)

    countries = doc.xpath("//table[contains(@class, 'wikitable')]/tbody/tr/td[1]/span/a/text()")
    links = doc.xpath("//table[contains(@class, 'wikitable')]/tbody/tr/td[1]/span/a/@href")

    start = 1
    end = 20

    for i in range(start, end):

        print("Name: " + countries[i])

        res = requests.get(PREFIX + links[i])
        doc = lxml.html.fromstring(res.content)

        a = doc.xpath("//table[contains(@class, 'infobox')]")

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

        except Exception:
            print("Fail in President or president place of birth")

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
        except Exception:
            print("Fail in Prime Minister or prime minister place of birth")

        try:
            c = a[0].xpath("//table//a[text()='Population']")

            if c:
                population = c[0].xpath("./../../following-sibling::tr[1]/td/text()")[0]
            else:
                c = a[0].xpath("//table//th[text()='Population']")
                population = c[0].xpath("./../following-sibling::tr[1]/td/text()")[0]
            print("Population: " + population.strip())
        except Exception:
            print("Fail in Population")

        try:
            d = a[0].xpath("//table//a[text()='Area ' or text()='Area']")

            if d:
                area = d[0].xpath("./../../following-sibling::tr[1]/td/text()")[0]
            else:
                d = a[0].xpath("//table//th[text()='Area ' or text()='Area']")
                area = d[0].xpath("./../following-sibling::tr[1]/td/text()")[0]

            print("Area: " + area)
        except Exception:
            print("Fail in Area")

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
            print("Government form: "+s[:-2])
        except Exception:
            print("Fail in Government Form")

        try:
            f = a[0].xpath("//table//th[text() = 'Capital' and @class = 'infobox-label']")
            capital = f[0].xpath("./../td/a/text()")[0]
            print("Capital: " + capital)
        except Exception:
            print("Fail in Capital")

        print("***************")

    print("Done")


def main():
    url = PREFIX + "/wiki/List_of_countries_by_population_(United_Nations)"

    get_countries(url)


if __name__ == "__main__":
    main()
