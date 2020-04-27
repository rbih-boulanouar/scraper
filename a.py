# -*- coding: utf-8 -*-

"""
    authors: RBIH BOULANOUAR ,LOUZE RIDHA

    python version 2.7

    script: articales_scraper.py

    requirements: beutifulsoup, requests, cfscrape, sys ,pandas

    notes:

        the keyword files (sport.csv,health.csv,science.csv) must be in the same directory with the script.
        the script may stop working sometimes because the used proxies are not stable.
        you may experience problems with encoding if u open csv files with microsoft excel, but it works on pycharm, liberoffice ....
        the script tested on linux mint 19 and windows 10

    what the script do?

        basically the script scrape 4 websites and get articles title, link , body if it's available in first page
        put all titles and links in csv file for each website
        organize articles by searching for keywords in the title or the body of article
        put the articles in result.csv by category

"""

#   import library

from bs4 import BeautifulSoup as bf
import requests, cfscrape, sys, os , time
import pandas as pd
from threading import Thread

#   function for write csv

def dataframe_to_csv(file, sport, health, science):
    #   create dictionary to save articles

    print("creating {}.csv ...".format(file))
    data = {
        "sport": sport,
        "health": health,
        "science": science
    }

    #   create dataframe

    df = pd.DataFrame.from_dict(data, orient="index")
    df = df.transpose()
    df.to_csv(r'{}.csv'.format(file), index=False)
    print("[+] {}.csv created [+]".format(file))


#   function for get proxies

def get_proxies():
    # Find a free proxy provider website
    # Scrape the proxies
    proxy_web_site = 'https://free-proxy-list.net/'
    response = requests.get(proxy_web_site)
    page_html = response.text
    page_soup = bf(page_html, "html.parser")
    containers = page_soup.find_all("div", {"class": "table-responsive"})[0]
    ip_index = [8 * k for k in range(80)]
    proxies = set()

    for i in ip_index:
        ip = containers.find_all("td")[i].text
        port = containers.find_all("td")[i + 1].text
        https = containers.find_all("td")[i + 6].text
        print("\nip address : {}".format(ip))
        print("port : {}".format(port))
        print("https : {}".format(https))

        if https == 'yes':
            proxy = ip + ':' + port
            proxies.add(proxy)

    return proxies


#   function for write one csv per website

def list_to_csv(mylist, name):
    print("creating {}.csv ...".format(name))
    myfile = open("{}.csv".format(name), "w")
    for j in mylist:
        myfile.write(j + "\n")
    myfile.close()
    print("[+] {}.csv created [+]".format(name))


#   function for check proxies

def check_proxies():
    # check the proxies and save the working ones

    proxies = get_proxies()
    test_url = 'https://httpbin.org/ip'
    for i in proxies:
        print("\nTrying to connect with proxy: {}".format(i))
        try:
            response = requests.get(test_url, proxies={"http": i, "https": i}, timeout=5)
            print("working proxy found")
            return i
            break
        except:
            print("Connnection error")
    return 0


#   function for articles category by keywords

def category(text, knum):
    #   open keyword files

    try:
        sport = open("sport.csv", "r")
        health = open("health.csv", "r")
        science = open("science.csv", "r")
    except:
        print("keywords files not found (sport.csv , health.csv, science.csv)")
        sys.exit(1)
    index = "None"
    i, j, h = 0, 0, 0

    #   check if keyword in article body or title

    for keyword in sport:
        keyword = keyword.strip().lower()
        if keyword in text.lower():
            i = i + 1
    for keyword in health:
        keyword = keyword.strip().lower()
        if keyword in text.lower():
            j = j + 1
    for keyword in science:
        keyword = keyword.strip().lower()
        if keyword in text.lower():
            h = h + 1

    #   check the category of most keywords exists in article

    if max(i, j, h) == i and i > knum:
        index = "sport"
    elif max(i, j, h) == j and j > knum:
        index = "health"
    elif max(i, j, h) == h and h > knum:
        index = "science"

    #   close keywords files

    sport.close()
    health.close()
    science.close()

    #   return the category of article

    return index

#   arrays for saving data

tsport, thealth, tscience = [], [], []

#   if website response code equal to 200
def scraper1():
    try:
        r1 = requests.get("https://www.liberte-algerie.com/actualite")
        unicode_str1 = r1.content.decode('utf8')
        encoded_str1 = unicode_str1.encode("utf-8")
    except:
        print("no working proxy found")
        return

    articles =[]
    if r1.status_code == 200:

        #   create beautiful soup object

        soup = bf(encoded_str1, "html.parser")

        #   get article title and body

        up_title = soup.find_all('strong', {'class': 'up-title'})
        title = soup.find_all('a', {'class': 'title'})
        body = soup.find_all("p")

        c = 0

        #   create tables to save articles

        for i in up_title:

            #   get link and article as text

            article = str(i.get_text().encode("utf-8")) + " " + str(title[c].get_text().encode("utf-8")) + " " + body[
                c].get_text().encode("utf-8")
            link = title[c]['href']
            articles.append(
                str(title[c].get_text().encode("utf-8") + ": " + "https://www.liberte-algerie.com" + str(link)).replace(",",
                                                                                                                        ""))

            if category(article, 3) == "sport":
                tsport.append(
                    str(title[c].get_text().encode("utf-8") + ": " + "https://www.liberte-algerie.com" + str(link)))
            elif category(article, 3) == "health":
                thealth.append(
                    str(title[c].get_text().encode("utf-8") + ": " + "https://www.liberte-algerie.com" + str(link)))
            elif category(article, 3) == "science":
                tscience.append(
                    str(title[c].get_text().encode("utf-8") + ": " + "https://www.liberte-algerie.com" + str(link)))

            c = c + 1

        list_to_csv(articles, "liberte-algerie")
        time.sleep(5)
        scraper1()


def scraper2():
    try:
        r2 = requests.get("https://www.elwatan.com/edition/actualite")
        unicode_str2 = r2.content.decode('utf8')
        encoded_str2 = unicode_str2.encode("utf-8")
    except:
        print("request failed try again")
        return

    articles = []
    if r2.status_code == 200:

        soup = bf(encoded_str2, "html.parser")
        title = soup.find_all('h3', {'class': 'title-14'})
        body = soup.find_all('div', {'class': 'p'})
        c=0
        for i in title:

            article = str(i.get_text().encode("utf-8") + ": " + body[c].get_text().encode("utf-8"))
            link = bf(str(i), "html.parser")
            link = link.find_all('a')
            link = link[0]["href"]
            articles.append(str(i.get_text().encode("utf-8") + ": " + str(link)).replace(",", ""))

            if category(article, 3) == "sport":
                tsport.append(str(i.get_text().encode("utf-8") + ": " + str(link)))
            elif category(article, 3) == "health":
                thealth.append(str(i.get_text().encode("utf-8") + ": " + str(link)))
            elif category(article, 3) == "science":
                tscience.append(str(i.get_text().encode("utf-8") + ": " + str(link)))

            c = c + 1

        list_to_csv(articles, "elwatan")
        time.sleep(5)
        scraper2()

def scraper3():
    try:
        r3 = requests.get("http://www.aps.dz")
        unicode_str3 = r3.content.decode('utf8')
        encoded_str3 = unicode_str3.encode("utf-8")
    except:
        print("request failed try again")
        return

    articles = []
    c=0
    if r3.status_code == 200:

        soup = bf(encoded_str3, "html.parser")
        title = soup.find_all("h3", {"class": "allmode-title"})

        for i in title:

            article = i.get_text().encode("utf-8")
            link = bf(str(i), "html.parser")
            link = link.find_all('a')
            link = link[0]['href']
            articles.append(str(i.get_text().encode("utf-8") + ": " + "http://www.aps.dz" + str(link)).replace(",", ""))

            if category(article, 1) == "sport":
                tsport.append(str(i.get_text().encode("utf-8") + ": " + "http://www.aps.dz" + str(link)))
            elif category(article, 1) == "health":
                thealth.append(str(i.get_text().encode("utf-8") + ": " + "http://www.aps.dz" + str(link)))
            elif category(article, 1) == "science":
                tscience.append(str(i.get_text().encode("utf-8") + ": " + "http://www.aps.dz" + str(link)))

            c = c + 1

        list_to_csv(articles, "aps")
        time.sleep(5)
        scraper3()
def scraper4():
    #   try to send a get request to the websites
    try:
        url = "https://tsa-algerie.com"
        working_proxy = check_proxies()
        if working_proxy != 0:
            scraper = cfscrape.create_scraper()
            proxies = {"http": working_proxy, "https": working_proxy}
            r4 = scraper.get(url, proxies=proxies, allow_redirects=True, timeout=(10, 20))
            unicode_str4 = r4.content.decode('utf8')
            encoded_str4 = unicode_str4.encode("utf-8")
        else:
            print("no working proxy found")

    #   if request failed
    except:
        print("request failed try again")
        scraper4()
    articles = []
    c=0
    if r4.status_code == 200:

        soup = bf(encoded_str4, "html.parser")
        title = soup.find_all('h2', {'class': 'ntdga__title transition'})
        body = soup.find_all('p', {'class': 'ntdga__desc'})

        for i in range(0, 10):

            article = title[i].get_text().encode("utf-8") + " " + body[i].get_text().encode("utf-8")
            link = bf(str(title[i].encode("utf-8")), "html.parser")
            link = link.find_all('a')
            link = link[0]["href"]
            articles.append(str(title[i].get_text().encode("utf-8") + ": " + str(link)).replace(",", ""))

            if category(article, 3) == "sport":
                tsport.append(str(title[i].get_text().encode("utf-8") + ": " + str(link)))
            elif category(article, 3) == "health":
                thealth.append(str(title[i].get_text().encode("utf-8") + ": " + str(link)))
            elif category(article, 3) == "science":
                tscience.append(str(title[i].get_text().encode("utf-8") + ": " + str(link)))

        list_to_csv(articles, "tsa")
        time.sleep(5)
        scraper4()

#   writing final result to csv

#schedule.every(10).minutes.do(job)
Thread(target = scraper1).start()
Thread(target = scraper2).start()
Thread(target = scraper3).start()
Thread(target = scraper4).start()
Thread(target = dataframe_to_csv("result", tsport, thealth, tscience)
).start()

