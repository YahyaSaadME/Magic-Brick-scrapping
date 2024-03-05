from bs4 import BeautifulSoup
import requests
import json
import numpy as np
import re

# Primary headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

s = requests.Session()
def get_datas(city,bhk,start=0):
    if start == 0 :
        with open(f"./dataset/BHK-{bhk}/{city}.json", 'w') as f:
            data = {'datas': []}
            json.dump(data, f, indent=4)
    
    soupOut = BeautifulSoup(s.get(f"https://www.magicbricks.com/property-for-sale/residential-real-estate?bedroom={bhk}&proptype=Multistorey-Apartment,Builder-Floor-Apartment,Penthouse,Studio-Apartment,Residential-House,Villa&cityName={city}").text, 'html.parser')
    totalIters = round(int(re.sub(r'\D', '', soupOut.find("div", class_="mb-srp__title--text1").text)) / 30)
    print("Total length:",totalIters*30)
    print("Total Iterations:",totalIters,"\nStarted Loading...")
    for i in range(1+start, totalIters + 1):
        try:
            soup = BeautifulSoup(s.get(f"https://www.magicbricks.com/property-for-sale/residential-real-estate?bedroom={bhk}&proptype=Multistorey-Apartment,Builder-Floor-Apartment,Penthouse,Studio-Apartment,Residential-House,Villa&page={str(i)}&cityName={city}").text, 'html.parser')
            if len(soup.find_all("div", class_="mb-srp__list")) != 0:
                for link in soup.find_all("div", class_="mb-srp__list"):
                    try:
                        get_content_of_each(city=city, link=str(json.loads(link.find_next("div").find("script").text)['url']),bhk=bhk)
                    except Exception as e:
                        print("Not added")
                print("added:", i, "data length:", len(soup.find_all("div", class_="mb-srp__list")))
        except Exception as e:
            # print("One Skipped")
            pass

def get_content_of_each(city, link,bhk):
    try:
        soupInner = BeautifulSoup(s.get(link, headers=headers).text, 'html.parser')
        all = {}
        title = soupInner.find("div", class_="mb-ldp__dtls__title").text
        price = soupInner.find("div", class_="mb-ldp__dtls__price").text
        card_summary = {}
        try: 
            for d in soupInner.find("div", class_="mb-ldp__dtls__body").find("ul", class_="mb-ldp__dtls__body__summary").find_all("li"):
                card_summary[d['data-icon']] = d.find("span", class_="mb-ldp__dtls__body__summary--highlight").text
        except Exception as e:
            pass
        
        card_list = {}
        try:
            for i in soupInner.find("div", class_="mb-ldp__dtls__body").find("ul", class_="mb-ldp__dtls__body__list").find_all("li", class_="mb-ldp__dtls__body__list--item"):
                card_list[i.find("div", class_="mb-srp__card__summary--label").text] = i.find("div", class_="mb-srp__card__summary--value").text
        except Exception as e:
            pass
        
        try:
            for j in soupInner.find("div", class_="mb-ldp__dtls__body").find("ul", class_="mb-ldp__dtls__body__list").find_all("li", class_="mb-ldp__dtls__body__list--item"):
                card_list[j.find("div", class_="mb-ldp__dtls__body__list--label").text] = j.find_next("div", class_="mb-ldp__dtls__body__list--value").text.split("sqft")[0]
        except Exception as e:
            pass   
        
        more_details ={}
        try:
            for k in soupInner.find("div", class_="mb-ldp__more-dtl").find("ul", class_="mb-ldp__more-dtl__list").find_all("li", class_="mb-ldp__more-dtl__list--item"):
                more_details[k.find("div", class_="mb-ldp__more-dtl__list--label").text] = k.find("div", class_="mb-ldp__more-dtl__list--value").text
        except Exception as e:
            pass
        
        amenities = []
        try:
            for l in soupInner.find("div", class_="mb-ldp__amenities").find("ul", class_="mb-ldp__amenities__list").find_all("li", class_="mb-ldp__amenities__list--item"):
                amenities.append(l.text)
        except Exception as e:
            pass
        
        try:
            with open(f'./dataset/BHK-{bhk}/{city}.json', 'r') as json_file:
                data = json.load(json_file)
                with open(f'./dataset/BHK-{bhk}/{city}.json', 'w') as json_file:
                    all['title'] = title
                    all['price'] = price
                    all['card summary'] = card_summary
                    all['card list'] = card_list
                    all['more details'] = more_details
                    all['amenities'] = amenities
                    data['datas'].append(all)
                    json.dump(data, json_file, indent=4) 
                    print("Added")
        except Exception as e:
            pass
    except Exception as e:
        print("e:", e)

get_datas(city=input("Enter city: "),bhk=input("Enter bhk:"),start=int(input("Enter starting iter:")))