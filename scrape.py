import re
import json
import pymongo
import requests
from bs4 import BeautifulSoup
from lxml import html

# myclient = pymongo.MongoClient("mongodb://localhost:27017/")
# mydb = myclient["phimlau_db"]
# print(myclient.list_database_names())


def getCrewData(url):
    crew_data = []
    r = requests.get(url=url)

    # Create a BeautifulSoup object
    soup = BeautifulSoup(r.text, 'html.parser')

    try:
        cast_list = soup.find("table", {"class": "cast_list"})

        trows = cast_list.find_all('tr')

        for tr in trows:
            td = tr.find_all('td')
            if len(td) == 4:
                row = [i.text for i in td]
                href = [i['href'] for i in td[0].find_all('a', href=True)]
                url = f"https://www.imdb.com{href[0]}"
                # soup =
                crew_data.append({
                    "name": re.sub("[^a-zA-Z()' ]+", '', row[1]).strip(),
                    "character": re.sub("[^a-zA-Z()' ]+", '', row[3]).strip(),
                    "info": f"https://www.imdb.com{href[0]}"
                })
    except Exception as e:
        print(e)
        return 
    return crew_data


apiGetAllIdMovies = requests.get("https://hls.hdv.fun/api/oldlist")
allMovies = json.loads(apiGetAllIdMovies.text)
for movie in allMovies:
    info = {}
    url = "https://hls.hdv.fun/imdb/"
    idDriveVideo = movie["imdb"]
    # idDriveVideo = "tt7286456"
    apiGetDetailMovie = requests.get(f"https://www.imdb.com/title/{idDriveVideo}")
    apiProductionCo = requests.get(f"https://www.imdb.com/title/{idDriveVideo}/companycredits?ref_=tt_dt_co")
    tree = html.fromstring(apiGetDetailMovie.content)
    soup = BeautifulSoup(apiGetDetailMovie.text, "html.parser")
    soup2 = BeautifulSoup(apiProductionCo.text, "html.parser")
    title = soup.title.text.split("-")[0]
    try:
        imdbRating = soup.find("div", attrs={"class": "imdbRating"}).text.strip().split("\n")
        subtext = re.sub(r"[^a-zA-Z|\d, ]", '', soup.find("div", {'class': 'subtext'}).text.strip())
        director = soup.find("div", attrs={"class": "credit_summary_item"}).text.strip().split("\n")[1]
        photoElement = soup.find("div",  attrs={"class": "poster"}).find_all("img", src=True)
        imdbPointVotes = imdbRating[0]
        imdbVotes = imdbRating[1]
        storyline = tree.xpath('//*[@id="titleStoryLine"]/div[1]/p/span')
        keywordsElement = tree.xpath('//*[@id="titleStoryLine"]/div[2]/a[*]/span')
        splitSubText = subtext.split('|')
        countriesElement = tree.xpath(
            '//*[@id="titleDetails"]/div[starts-with(@class, "txt-block")]/a[starts-with(@href, "/search/title?country")]')
        languageElement = tree.xpath(
            '//*[@id="titleDetails"]/div[starts-with(@class, "txt-block")]/a[starts-with(@href, "/search/title?title_type")]')
        runtimeElement = tree.xpath('//*[@id="title-overview-widget"]/div[1]/div[2]/div/div[2]/div[2]/div/time')
        keywords = [keyword.text for keyword in keywordsElement]
        genres = [genre for genre in splitSubText[-2].split(',')]
        countries = [country.text for country in countriesElement]
        languages = [language.text for language in languageElement]
        releaseDate = splitSubText[-1]
        productionCo = [company.text for company in soup2.find_all("ul", attrs={"class": "simpleList"})[0].find_all('a')]
        runtime = [re.sub(r'\n', '', rt.text.strip()) for rt in runtimeElement]
        photo = [i['src'] for i in photoElement]
        info["id"] = idDriveVideo
        info["title"] = title
        info["titleSlug"] = 'N/A'
        info["photos"] = photo
        info["trailer"] = 'N/A'
        info["episode"] = f'https://hls.hdv.fun/imdb/{idDriveVideo}'
        info['status'] = 'N/A'
        info["views"] = 'N/A'
        info["imdbVoted"] = imdbPointVotes
        info["pointsVoted"] = imdbVotes
        info["subtext"] = subtext
        info["director"] = director
        info["cast"] = getCrewData(f"https://www.imdb.com/title/{idDriveVideo}")
        info["storyline"] = storyline[0].text.strip()
        info["keywords"] = keywords
        info["genres"] = genres
        info["country"] = countries
        info["language"] = languages
        info["releaseDate"] = releaseDate
        info["producers"] = productionCo
        info["runtime"] = runtime
        info["showTimes"] = 'N/A'

    except Exception as e:
        print(e)
        return 
    result = json.dumps(info, indent=4)
    with open("data.txt", "a") as f:
        f.writelines(f"{result} \n")
        print("done")
