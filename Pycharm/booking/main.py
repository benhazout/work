from bs4 import BeautifulSoup
import requests, os
import config
from services import log
from concurrent.futures import ThreadPoolExecutor, as_completed

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

logger = log.get_logger('main.py')

booking_url = os.environ.get('BOOKING_URL')
booking_country_url = os.environ.get('BOOKING_COUNTRY_URL')


def get_countries():
    """
    :return: dictionary of all countries listed in booking.com as keys and their url as the value
    """
    try:
        global booking_country_url, booking_url
        page_results = requests.get(booking_country_url, headers=headers)
        if page_results:
            soup = BeautifulSoup(page_results.text, 'html.parser')
            country_lists = soup.find_all("li", {"class": "dest-sitemap__subsublist-item"}, "a")
            country_dict = {}
            for li in country_lists:
                for country in li.find_all("a"):
                    country_dict[country.text.strip()] = booking_url + country['href'].split('?')[0]
            return country_dict
        else:
            logger.error('request failed')
            return Falsei
    except Exception as e:
        logger.error(e)
        return False


def get_cities(country_url):
    """

    :param country_url: url of country
    :return: dictionary of all cities listed in a country as keys and their url as the value
    """
    try:
        global booking_url
        page_results = requests.get(country_url, headers=headers)
        if page_results:
            soup = BeautifulSoup(page_results.text, 'html.parser')
            cities_lists = soup.find_all("li", {"class": "dest-sitemap__subsublist-item"}, "a")
            cities_dict = {}
            for li in cities_lists:
                for city in li.find_all("a"):
                    cities_dict[city.text.strip()] = booking_url + city['href'].split('?')[0]
            return cities_dict
        else:
            logger.error('request failed')
            return False
    except Exception as e:
        print(e)
        return False


# edited to return number of hotels
def get_hotels(city_url):
    """

    :param city_url: url of city
    :return: dictionary of all hotels listed in a city as keys and their url as the value
    """

    try:
        global booking_url
        page_results = requests.get(city_url, headers=headers)
        if page_results:
            soup = BeautifulSoup(page_results.text, 'html.parser')
            city_results_lists = soup.find_all("li", {"class": "dest-sitemap__list-item"})
            hotels_dict = {}
            for city_result_li in city_results_lists:
                for header_3 in city_result_li.find_all("h3"):
                    for header in header_3:
                        if header.split(' ')[0] == 'Hotels' and header.split(' ')[1] == 'in':
                            # print(header)
                            hotels = city_result_li.find_all("li", {"class": "dest-sitemap__subsublist-item"}, "a")
                            print(header, len(hotels))
                            return len(hotels)  # edit ------------

            #                             for li in hotels:
            #                                 for hotel in li.find_all("a"):
            #                                     hotels_dict[hotel.text.strip()] = booking_url + hotel['href'].split('?')[0]

            # return hotels_dict
            #             print(count)
            return 0
        else:
            logger.error('request failed')
            return False
    except Exception as e:
        print(e)
        return False


def get_hotel_data(hotel_name, hotel_url):
    """

        :param hotel_name: hotel name
        :param hotel_url: url of hotel
        :return: dictionary of all cities listed in a country as keys and their url as the value
        """
    try:
        global booking_url
        page_results = requests.get(hotel_url, headers=headers)
        if page_results:
            soup = BeautifulSoup(page_results.text, 'html.parser')
            hotel_address = soup.find("span", {"class": "hp_address_subtitle js-hp_address_subtitle jq_tooltip"})
            hotel_description = []
            hotel_description_soup = soup.find("div", {"id": "property_description_content"})
            if hotel_description_soup:
                for p in hotel_description_soup.find_all("p"):
                    if not p.find("span"):
                        hotel_description.append(p.text)
            des = " ".join(hotel_description)
            all_facilities = {}
            facilities_lists = soup.find_all("div", {"class": "facilitiesChecklistSection"})
            # soup
            for facility_section in facilities_lists:
                facility_name = facility_section.find("h5").text.strip()
                all_facilities[facility_name] = []
                for li in facility_section.find_all("li"):
                    facility_with_span = li.find_all("span", {"data-name-en": True})
                    if facility_with_span:
                        for facility in facility_with_span:
                            all_facilities[facility_name].append(facility.text.strip().replace('\n', ''))
                    else:
                        all_facilities[facility_name].append(li.text.strip().replace('\n', ''))

            all_most_popular_facilities = []
            most_popular_facilities = soup.find_all("div", {"class": "important_facility"}, "data-name-en")
            for facility in most_popular_facilities:
                all_most_popular_facilities.append(facility.text.strip().replace('\n', ''))

            all_property_surroundings = {}
            property_surroundings = soup.find_all("div", {"class": "hp_location_block__section_container"})
            for surrounding in property_surroundings:
                surrounding_name = surrounding.find("span")
                if surrounding_name:
                    for li in surrounding.find_all("li"):
                        location_name = li.find("div", {"class": "bui-list__description"}).text.strip().replace('\n',
                                                                                                                '')
                        location_distance = li.find("div", {
                            "class": "bui-list__item-action hp_location_block__section_list_distance"}).text.strip().replace(
                            '\n', '')

                        all_property_surroundings[surrounding_name.text.strip()] = {'location_name': location_name,
                                                                                    'location_distance': location_distance}
            score = float(soup.find("div", {"class": "e5a32fd86b"}).text)
            amount_of_reviews = float(soup.find("div", {"class": "_6a1b6ff88e"}).text.split(' ')[0])

            top_three_comments = []
            comments = soup.find("ul", {"class": "bui-carousel__inner"})
            if comments:
                lis = comments.find_all("div", {"class": "c-review-snippet"})
                for i in range(len(lis)):
                    if 2 < i:
                        break
                    name = lis[i].find("span", {"class": "bui-avatar-block__title"}).text.strip()
                    comment = lis[i].find("span", {"class": "c-review__body"}).text.strip()
                    top_three_comments.append({'name': name, 'comment': comment})

            geometry = {}
            coordinates_fetch = soup.find("a", {"id": "hotel_sidebar_static_map"})["data-atlas-latlng"].split(',')
            if coordinates_fetch:
                geometry['type'] = 'Point'
                geometry['coordinates'] = [float(coordinates_fetch[1]), float(coordinates_fetch[0])]

            return {'type': 'Feature',
                    'geometry': geometry,
                    'properties': {
                        'name': hotel_name,
                        'address': hotel_address.text.strip().replace('\n', ''),
                        'description': des,
                        'facilities': all_facilities,
                        'most_popular_facilities': list(set(all_most_popular_facilities)),
                        'property_surroundings': all_property_surroundings,
                        'score': score,
                        'amount_of_reviews': amount_of_reviews,
                        'top_three_comments': top_three_comments
                    }

                    }
        else:
            logger.error('request failed')
            return False
    except Exception as e:
        print(e)
        return False


def get_all_in_country(country):
    all_countries = get_countries()
    if country not in all_countries:
        return False
    all_cities = get_cities(all_countries[country])
    processes = []
    with ThreadPoolExecutor() as executer:

        for city in all_cities.keys():
            processes.append(executer.submit(get_hotels, all_cities[city]))
    hotels = []
    for task in as_completed(processes):
        if task.result():
            hotels.append(task.result())

    return sum(hotels)


print(os.environ.get('BOOKING_COUNTRY_URL'))
#cont = get_countries()
#print(cont)
#isra = get_cities('http://www.booking.com/destination/country/il.en-gb.html')
#print(isra)
#arbel = get_hotels('http://www.booking.com/destination/city/il/arbel.en-gb.html')
#print(len(arbel))
# arb_data = get_hotel_data('Arbel Guest House Shavit Family', 'http://www.booking.com/hotel/il/arbel-guest-house.en-gb.html')
# print(arb_data)
ff = get_all_in_country('Germany')
print(len(ff))
co = 0
for f in ff:
    co += len(f)
print(co)