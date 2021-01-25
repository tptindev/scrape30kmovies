import re
import json
import pymongo
import requests
from bs4 import BeautifulSoup
from lxml import html

client = pymongo.MongoClient("mongodb+srv://vku:vku@lauc2t.4pp7l.mongodb.net/lauc2t?retryWrites=true&w=majority")
db = client.lauc2t
movies_collection = db.movies
directors_collection = db.directors
stars_collection = db.stars
categories_collection = db.categories
countries_collection = db.countries
languages_collection = db.languages
producers_collection = db.producers
keywords_collection = db.keywords


def no_accent_vietnamese(s):
    s = re.sub(r'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', s)
    s = re.sub(r'[ÀÁẠẢÃĂẰẮẶẲẴÂẦẤẬẨẪ]', 'A', s)
    s = re.sub(r'[èéẹẻẽêềếệểễ]', 'e', s)
    s = re.sub(r'[ÈÉẸẺẼÊỀẾỆỂỄ]', 'E', s)
    s = re.sub(r'[òóọỏõôồốộổỗơờớợởỡ]', 'o', s)
    s = re.sub(r'[ÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠ]', 'O', s)
    s = re.sub(r'[ìíịỉĩ]', 'i', s)
    s = re.sub(r'[ÌÍỊỈĨ]', 'I', s)
    s = re.sub(r'[ùúụủũưừứựửữ]', 'u', s)
    s = re.sub(r'[ƯỪỨỰỬỮÙÚỤỦŨ]', 'U', s)
    s = re.sub(r'[ỳýỵỷỹ]', 'y', s)
    s = re.sub(r'[ỲÝỴỶỸ]', 'Y', s)
    s = re.sub(r'[Đ]', 'D', s)
    s = re.sub(r'[đ]', 'd', s)
    s = re.sub(r'[(]', '-', s)
    s = re.sub(r'[):]', '', s)
    s = re.sub(r'\s', '-', s)
    return s.lower()


def getCrewData(url):
    crew_data = []
    stars_ls = []
    info_star = {}
    r = requests.get(url=url)

    # Create a BeautifulSoup object
    soup = BeautifulSoup(r.text, 'html.parser')

    cast_list = soup.find("table", {"class": "cast_list"})

    trows = cast_list.find_all('tr')

    for tr in trows:
        td = tr.find_all('td')
        if len(td) == 4:
            row = [i.text for i in td]
            href = [i['href'] for i in td[0].find_all('a', href=True)]
            url = f"https://www.imdb.com{href[0]}bio?ref_=nm_ov_bio_sm"
            r = requests.get(url)
            soup1 = BeautifulSoup(r.text, 'html.parser')
            try:
                name = soup1.find('div', attrs={"class": "parent"}).find('a').text.strip()
                info_star["name"] = name
                try:
                    photo = soup1.find('img', attrs={"class": "poster"}, src=True)['src']
                    info_star["photo"] = photo
                    try:
                        bio = soup1.find('div', attrs={"class": "soda odd"}).find_all('p')[0].text.strip()
                        info_star["bio"] = bio
                    except Exception:
                        bio = ''
                        info_star["bio"] = bio
                except Exception:
                    photo = ''
                    info_star["photo"] = photo
            except Exception:
                name = ''
                info_star["name"] = name
            result = stars_collection.find_one({"name": info_star["name"]})
            if result:
                stars_ls.append({"_id": result['_id']})
            else:
                star = stars_collection.insert_one(dict(info_star))
                stars_ls.append({"_id": star.inserted_id})
            crew_data.append({
                "name": re.sub("[^a-zA-Z()' ]+", '', row[1]).strip(),
                "character": re.sub("[^a-zA-Z()' ]+", '', row[3]).strip(),
                "info": f"https://www.imdb.com{href[0]}"
            })

    return stars_ls


def get_directors(url):
    directors_ls = []
    directors_info = {}
    request = requests.get(url)
    soup = BeautifulSoup(request.text, 'html.parser')
    try:
        name = soup.find('div', attrs={"class": "parent"}).find('a').text.strip()
        directors_info["name"] = name
        try:
            photo = soup.find('img', attrs={"class": "poster"}, src=True)['src']
            directors_info["photo"] = photo
            try:
                bio = soup.find('div', attrs={"class": "soda odd"}).find_all('p')[0].text.strip()
                directors_info["bio"] = bio
            except Exception:
                bio = ''
                directors_info["bio"] = bio
        except Exception:
            photo = ''
            directors_info["photo"] = photo
    except Exception:
        name = ''
        directors_info["name"]= name
    result = stars_collection.find_one({"name": directors_info["name"]})
    if result:
        directors_ls.append({"_id": result['_id']})
    else:
        star = stars_collection.insert_one(dict(directors_info))
        directors_ls.append({"_id": star.inserted_id})
    return directors_ls



# idDriveVideo = "tt7286456"
# getCrewData(f"https://www.imdb.com/title/{idDriveVideo}")

apiGetAllIdMovies = requests.get("https://hls.hdv.fun/api/oldlist")
allMovies = json.loads(apiGetAllIdMovies.text)
for index, movie in enumerate(allMovies):
    info = {}
    ls_categories = []
    ls_countries = []
    ls_languages = []
    ls_producers = []
    ls_keywords = []
    url = "https://hls.hdv.fun/imdb/"
    idDriveVideo = movie["imdb"]
    # idDriveVideo = "tt7286456"
    apiGetDetailMovie = requests.get(f"https://www.imdb.com/title/{idDriveVideo}")
    apiProductionCo = requests.get(f"https://www.imdb.com/title/{idDriveVideo}/companycredits?ref_=tt_dt_co")
    tree = html.fromstring(apiGetDetailMovie.content)
    soup = BeautifulSoup(apiGetDetailMovie.text, "html.parser")
    soup2 = BeautifulSoup(apiProductionCo.text, "html.parser")
    title = soup.title.text.split("-")[0]
    stars = getCrewData(f"https://www.imdb.com/title/{idDriveVideo}")
    try:
        imdbRating = soup.find("div", attrs={"class": "imdbRating"}).text.strip().split("\n")
        subtext = re.sub(r"[^a-zA-Z|\d, ]", '', soup.find("div", {'class': 'subtext'}).text.strip())
        director = soup.find("div", attrs={"class": "credit_summary_item"}).text.strip().split("\n")[1]
        director_href = soup.find("div", attrs={"class": "credit_summary_item"}).find('a', href=True)['href']
        ls_directories = get_directors(f"https://www.imdb.com{director_href}bio?ref_=nm_ov_bio_sm")
        photoElement = soup.find("div", attrs={"class": "poster"}).find_all("img", src=True)
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
        keywords = [keyword.text.strip() for keyword in keywordsElement]
        for i in keywords:
            dictKeyword = {
                "name": i,
                "slug": no_accent_vietnamese(i)
            }
            result = keywords_collection.find_one({"name": i})
            if result:
                ls_keywords.append({"_id": result['_id']})
            else:
                kd = keywords_collection.insert_one(dictKeyword)
                ls_keywords.append({"_id": kd.inserted_id})
        genres = [genre.strip() for genre in splitSubText[-2].split(',')]
        for i in genres:
            dictGenres = {
                "name": i,
                "slug": no_accent_vietnamese(i)
            }
            result = categories_collection.find_one({"name": i})
            if result:
                ls_categories.append({"_id": result['_id']})
            else:
                category = categories_collection.insert_one(dictGenres)
                ls_categories.append({"_id": category.inserted_id})

        countries = [country.text.strip() for country in countriesElement]
        for i in countries:
            dictCountries = {
                "name": i,
                "slug": no_accent_vietnamese(i)
            }
            result = countries_collection.find_one({"name": i})
            if result:
                ls_countries.append({"_id": result['_id']})
            else:
                country = countries_collection.insert_one(dictCountries)
                ls_countries.append({"_id": country.inserted_id})
        languages = [language.text for language in languageElement]
        for i in languages:
            dictLanguage = {
                "name": i
            }
            result = languages_collection.find_one({"name": i})
            if result:
                ls_languages.append({"_id": result['_id']})
            else:
                language = languages_collection.insert_one(dictLanguage)
                ls_languages.append({"_id": language.inserted_id})
        releaseDate = splitSubText[-1]
        productionCo = [company.text.strip() for company in
                        soup2.find_all("ul", attrs={"class": "simpleList"})[0].find_all('a')]
        for i in productionCo:
            dictProducer = {
                "name": i,
                "contact": {
                    "phone": "",
                    "email": ""
                },
                "address": "",
                "country": ""
            }
            result = producers_collection.find_one({"name": i})
            if result:
                ls_producers.append({"_id": result['_id']})
            else:
                country = producers_collection.insert_one(dictProducer)
                ls_producers.append({"_id": country.inserted_id})

        runtime = [re.sub(r'\n', '', rt.text.strip()) for rt in runtimeElement]
        photo = [i['src'] for i in photoElement]
        # info["id"] = idDriveVideo
        info["title"] = title
        info["titleSlug"] = 'N/A'
        info["photos"] = photo
        info["trailer"] = 'N/A'
        info["episode"] = f'https://hls.hdv.fun/imdb/{idDriveVideo}'
        info['status'] = 'Done'
        info["views"] = 0
        info["imdbVoted"] = imdbPointVotes
        info["pointsVoted"] = imdbVotes
        info["director"] = ls_directories
        info["stars"] = stars
        info["storyline"] = storyline[0].text.strip()
        info["keywords"] = ls_keywords
        info["categories"] = ls_categories
        info["countries"] = ls_countries
        info["languages"] = ls_languages
        info["releaseDate"] = releaseDate
        info["producers"] = ls_producers
        info["runtime"] = runtime[0]
        info["showTimes"] = 'N/A'

    except Exception as e:
        print(e)
    movies_collection.insert_one(dict(info))
    print(f"Saved - {index}")
    import time
    import os
    import platform
    time.sleep(0.2)
    if platform.system().lower() == "windows":
        os.system("cls")
    else:
        os.system("clear")