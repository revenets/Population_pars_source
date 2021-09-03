import requests
from bs4 import BeautifulSoup
from Docker_project.app import db, Region, Country


URL = "https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population"
HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "accept": "*/*"
}


def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_content(html):
    soup = BeautifulSoup(html, "html.parser")
    items = soup.find("table", class_="wikitable").find_all("tr")[2:]

    wikitable = []

    for item in items:
        wikitable.append({
            "Country": item.find_all("td")[0].find_all("a")[0].get_text(),
            "Region": item.find_all("td")[1].find("a").get_text(),
            "Population": int("".join(item.find_all("td")[2].get_text().split(",")))
        })

    return wikitable


def parse():
    html = get_html(URL)
    if html.status_code == 200:
        db.create_all()
        population = get_content(html.text)
        regions = set()
        for el in population:
            regions.add(el["Region"])
        items = [Region(name=i) for i in list(regions)]
        # print([str(el) for el in items])

        items2 = []
        for el in population:
            for region in regions:
                if el["Region"] == region:
                    items2.append(Country(name=el["Country"], region=[i for i in items if str(i) == region][0],
                                          population=el["Population"]))

        db.session.add_all(items)
        db.session.add_all(items2)
        db.session.commit()

    else:
        print("Error")


if __name__ == '__main__':
    parse()


