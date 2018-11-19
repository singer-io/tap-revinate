#!/usr/bin/env python3

from decimal import Decimal
import hmac
import hashlib
import base64
import binascii
import re
import copy
import datetime
import json
import os
import sys
import time
import logging
import dateutil.parser
import requests
import singer
from singer import utils
import backoff
import tap_revinate.schemas as schemas

LOGGER = singer.get_logger()
BASE_URL = 'https://porter.revinate.com'
REQUIRED_CONFIG_KEYS = ['username',
                        'api_key',
                        'api_secret',
                        'start_date']
CONFIG = {
    'username': None,
    'api_key': None,
    'api_secret': None,
    'start_date': None
}
STATE = {}

@backoff.on_exception(backoff.expo,
                      (requests.exceptions.RequestException),
                      max_tries=5,
                      giveup=lambda e: e.response is not None and 400 <= e.response.status_code < 500, # pylint: disable=line-too-long
                      factor=2)

def request(url, headers, params={}):
    LOGGER.info("Making request: GET {} {}".format(url, params))
    try:
        response = requests.get(
            url=url,
            headers=headers,
            params=params)
    except Exception as exception:
        LOGGER.exception(exception)
    LOGGER.info("Got response code: {}".format(response.status_code))
    response.raise_for_status()
    return response

def parse_review(review):
    # flatten review links and get review_id and hotel_id
    review_url = ''
    review_id = 0
    hotel_url = ''
    hotel_id = 0
    if 'links' not in review:
        links_json = {}
    else:
        links_json = review['links']
    for link in review['links']:
        if link['rel'] == "self":
            review_url = link['href']
            match = re.search(r".*/reviews/(.*)", review_url)
            if match:
                review_id = int(match.group(1))
            else:
                review_id = 0
        if link['rel'] == "hotel":
            hotel_url = link['href']
            match = re.search(r".*/hotels/(.*)", hotel_url)
            if match:
                hotel_id = int(match.group(1))
            else:
                hotel_id = 0
    # flatten review_site links and get review_site_id
    if 'reviewSite' not in review:
        review_site_json = {}
    else:
        review_site_json = review['reviewSite']
    review_site_url = ''
    review_site_id = 0
    for link in review['reviewSite']['links']:
        if link['rel'] == "self":
            review_site_url = link['href']
            match = re.search(r".*/reviewsites/(.*)", review_site_url)
            if match:
                review_site_id = int(match.group(1))
            else:
                review_site_id = 0
    # flatten language links and get language_id
    language_url = ''
    language_id = 0
    if 'language' not in review:
        language_json = {}
    else:
        language_json = review['language']

        for link in review['language']['links']:
            if link['rel'] == "self":
                language_url = link['href']
            match = re.search(r".*/languages/(.*)", language_url)
            if match:
                language_id = int(match.group(1))
            else:
                language_id = 0
    # Get other nested json elements
    if 'subratings' not in review:
        subratings_json = {}
    else:
        subratings_json = review['subratings']
    if 'guestStay' not in review:
        guest_stay_json = {}
    else:
        guest_stay_json = review['guestStay']
    if 'surveyTopics' not in review:
        survey_topics_json = {}
    else:
        survey_topics_json = review['surveyTopics']
    if 'response' not in review:
        response_json = {}
    else:
        response_json = review['response']
    return {
        'review_id': int(review_id),
        'review_url': str(review_url),
        'review_json': str(review),
        'hotel_id': int(hotel_id),
        'hotel_url': str(hotel_url),
        'title': str(review.get('title', '')).replace('"', '\\"').replace('\r', \
            '').replace('\n', ''),
        'body': str(review.get('body', '')).replace('"', '\\"').replace('\r', \
            '').replace('\n', ''),
        'author': str(review.get('author', '')),
        'author_location': str(review.get('authorLocation', '')),
        'date_review': int(review.get('dateReview', 0)),
        'date_collected': int(review.get('dateCollected', 0)),
        'updated_at': int(review.get('updatedAt', 0)),
        'rating': float(review.get('rating', 0.0)),
        'nps': int(review.get('nps', 0)),
        'review_site_json': str(review_site_json),
        'review_site_id': int(review_site_id),
        'review_site_url': str(review_site_url),
        'review_site_name': str(review.get('reviewSite', {}).get('name', '')),
        'review_site_main_url': str(review.get('reviewSite', {}).get('mainUrl', '')),
        'review_site_slug': str(review.get('reviewSite', {}).get('slug', '')),
        'language_json': str(language_json),
        'language_id': int(language_id),
        'language_url': str(language_url),
        'language_name': str(review.get('language', {}).get('name', '')),
        'language_english_name': str(review.get('language', {}).get('englishName', '')),
        'language_slug': str(review.get('language', {}).get('slug', '')),
        'crawled_url': str(review.get('crawledUrl', '')),
        'subratings_json': str(subratings_json),
        'subratings_cleanliness': float(review.get('subratings', {}).get('Cleanliness', 0.0)),
        'subratings_hotel_condition': float(review.get('subratings', \
            {}).get('Hotel condition', 0.0)),
        'subratings_rooms': float(review.get('subratings', {}).get('Rooms', 0.0)),
        'subratings_service': float(review.get('subratings', {}).get('Service', 0.0)),
        'trip_type': str(review.get('tripType', '')),
        'guest_stay_json': str(guest_stay_json),
        'survey_topics_json': str(survey_topics_json),
        'response_json': str(response_json),
        'links_json': str(links_json)
    }

def fetch_reviews(headers, params):
    url = '{}/reviews'.format(BASE_URL)
    resp = request(url, headers, params)
    parsed = json.loads(resp.text)
    return parsed

def sync_reviews(headers, CONFIG, STATE):
    page = 0 # initialize at first page
    rec = 1 # initialize first record
    total_pages = 1 # initial total pages, which gets overwritten
    total_elements = 0 # initial total elements, which gets overwritten
    size = 10 # number of records per request
    to_timestamp = int(headers['X-Revinate-Porter-Timestamp'])
    last_update = to_timestamp  # init
    from_timestamp = 0  # initial value
    # set from_timestamp as NVL(STATE.last_update, CONFIG.start_date, now - 1 year)
    if 'last_update' not in STATE:
        if 'start_date' not in CONFIG:
            from_timestamp = to_timestamp - (60 * 60 * 24 * 7)  # looks back 1 week
        else:
            from_timestamp = int(time.mktime(datetime.datetime.strptime(CONFIG['start_date'], \
                '%Y-%m-%dT%H:%M:%SZ').timetuple()))
    else:
        from_timestamp = int(STATE['last_update'])
    updated_at_range = str(from_timestamp) + '..' + str(to_timestamp)
    # loop thru all pages
    while (page + 1) <= total_pages:
        if (rec + size) <= total_elements:
            rec_to = rec + size - 1
        else:
            rec_to = total_elements
        LOGGER.info('Page {} of {} Total Pages, Record {}-{} of {} Total Records'.format( \
            str(page + 1), str(total_pages), str(rec), str(rec_to), str(total_elements)))
        params = {
            'updatedAt': updated_at_range,
            'page': page,
            'size': size,
            'sort': 'updatedAt,ASC'
        }
        try:
            reviews_parsed = fetch_reviews(headers, params)
        except Exception as exception:
            LOGGER.exception(exception)
            break
        # loop thru all records on page
        for record in reviews_parsed['content']:
            parsed_review = parse_review(record)
            singer.write_record('reviews', parsed_review)
            last_update = record['updatedAt']
            rec = rec + 1
        page_json = reviews_parsed['page']
        total_pages = int(page_json.get('totalPages', 1))
        total_elements = int(page_json.get('totalElements', 0))
        page = page + 1
    # update STATE last_update
    utils.update_state(STATE, 'last_update', last_update)
    singer.write_state(STATE)
    LOGGER.info("State synced to last_update: {}".format(last_update))
    LOGGER.info("Done syncing reviews.")

def parse_hotel_reviews_snapshot_by_time(hotel_id, hotel_reviews_snapshot_url, period):
    if 'values' not in period:
        values_json = {}
    else:
        values_json = period['values']
    return {
        'hotel_id': int(hotel_id),
        'hotel_reviews_snapshot_url': str(hotel_reviews_snapshot_url),
        'time_period_json': str(period),
        'unix_time': int(period.get('time', 0)),
        'values_json': str(values_json),
        'snapshot_average_rating': float(period.get('values', {}).get('averageRating', 0.0)),
        'snapshot_new_reviews': float(period.get('values', {}).get('newReviews', 0.0)),
        'snapshot_pos_reviews_pct': float(period.get('values', {}).get('posReviewsPct', 0.0)),
        'snapshot_trip_advisor_market_ranking': int(period.get('values', \
            {}).get('tripadvisorMarketRanking', 0)),
        'snapshot_trip_advisor_market_ranking_pctl': float(period.get('values', \
            {}).get('tripadvisorMarketRankingPctl', 0.0)),
        'snapshot_trip_advisor_market_size': int(period.get('values', \
            {}).get('tripadvisorMarketSize', 0)),
    }

def parse_hotel_reviews_snapshot_by_site(hotel_id, hotel_reviews_snapshot_url, \
    start_date, end_date, site):
    # flatten review_site links and get review_site_id
    review_site_url = ''
    review_site_id = 0
    if 'reviewSite' not in site:
        review_site_json = {}
    else:
        review_site_json = site['reviewSite']
        for link in site['reviewSite']['links']:
            if link['rel'] == "self":
                review_site_url = link['href']
                match = re.search(r".*/reviewsites/(.*)", review_site_url)
                if match:
                    review_site_id = int(match.group(1))
                else:
                    review_site_id = 0
    if 'values' not in site:
        values_json = {}
    else:
        values_json = site['values']
    return {
        'hotel_id': int(hotel_id),
        'hotel_reviews_snapshot_url': str(hotel_reviews_snapshot_url),
        'site_json': str(site),
        'snapshot_start_date': int(start_date),
        'snapshot_end_date': int(end_date),
        'review_site_json': str(review_site_json),
        'review_site_id': int(review_site_id),
        'review_site_url': str(review_site_url),
        'review_site_name': str(site.get('reviewSite', {}).get('name', '')),
        'review_site_main_url': str(site.get('reviewSite', {}).get('mainUrl', '')),
        'review_site_slug': str(site.get('reviewSite', {}).get('slug', '')),
        'values_json': str(values_json),
        'site_average_rating': float(site.get('values', {}).get('averageRating', 0.0)),
        'site_new_reviews': float(site.get('values', {}).get('newReviews', 0.0)),
        'site_pos_reviews_pct': float(site.get('values', {}).get('posReviewsPct', 0.0)),
        'site_trip_advisor_market_ranking': int(site.get('values', \
            {}).get('tripadvisorMarketRanking', 0)),
        'site_trip_advisor_market_ranking_pctl': float(site.get('values', \
            {}).get('tripadvisorMarketRankingPctl', 0.0)),
        'site_trip_advisor_market_size': int(site.get('values', \
            {}).get('tripadvisorMarketSize', 0))
    }

def parse_hotel_reviews_snapshot(snapshot, hotel_id):
    # flatten links and get start/end dates
    hotel_reviews_snapshot_url = ''
    start_date = 0
    end_date = 0
    if 'links' not in snapshot:
        links_json = {}
    else:
        links_json = snapshot['links']
        for link in snapshot['links']:
            if link['rel'] == "self":
                hotel_reviews_snapshot_url = link['href']
                start_date = int(re.findall('^.*' + r'\?date' + r'\=(' + r'\d+)' + \
                    r'\.' + r'\.' + r'\d+$', hotel_reviews_snapshot_url)[0])
                end_date = int(re.findall('^.*' + r'\?date' + r'\=' + r'\d+' + r'\.' \
                    + r'\.(' + r'\d+)$', hotel_reviews_snapshot_url)[0])
    # Get other nested json elements
    if 'aggregateValues' not in snapshot:
        aggregate_values_json = {}
    else:
        aggregate_values_json = snapshot['aggregateValues']
    if 'valuesByReviewSite' not in snapshot:
        values_by_review_site_json = {}
    else:
        values_by_review_site_json = snapshot['valuesByReviewSite']
    if 'valuesByTime' not in snapshot:
        values_by_time_json = {}
    else:
        values_by_time_json = snapshot['valuesByTime']
    return {
        'hotel_id': int(hotel_id),
        'hotel_reviews_snapshot_url': str(hotel_reviews_snapshot_url),
        'hotel_reviews_snapshot_json': str(snapshot),
        'snapshot_start_date': int(start_date),
        'snapshot_end_date': int(end_date),
        'aggregate_values_json': str(aggregate_values_json),
        'aggregate_average_rating': float(snapshot.get('aggregateValues', \
            {}).get('averageRating', 0.0)),
        'aggregate_new_reviews': float(snapshot.get('aggregateValues', \
            {}).get('newReviews', 0.0)),
        'aggregate_pos_reviews_pct': float(snapshot.get('aggregateValues', \
            {}).get('posReviewsPct', 0.0)),
        'aggregate_trip_advisor_market_ranking': int(snapshot.get('aggregateValues', \
            {}).get('tripadvisorMarketRanking', 0)),
        'aggregate_trip_advisor_market_ranking_pctl': float(snapshot.get('aggregateValues', \
            {}).get('tripadvisorMarketRankingPctl', 0.0)),
        'aggregate_trip_advisor_market_size': int(snapshot.get('aggregateValues', \
            {}).get('tripadvisorMarketSize', 0)),
        'values_by_review_site_json': str(values_by_review_site_json),
        'values_by_time_json': str(values_by_time_json),
        'links_json': str(links_json)
    }

def fetch_hotel_reviews_snapshot(headers, hotel_id):
    url = '{}/hotels/{}/reviewssnapshot'.format(BASE_URL, str(hotel_id))
    resp = request(url, headers)
    parsed = json.loads(resp.text)
    return parsed

def sync_hotel_reviews_snapshot(headers, hotel_id):
    hotel_reviews_snapshot = fetch_hotel_reviews_snapshot(headers, hotel_id)
    hotels_reviews_snapshot_parsed = hotel_reviews_snapshot
    LOGGER.info('Synced hotel reviews snapshot for hotel_id: {}.'.format(hotel_id))
    snapshot = parse_hotel_reviews_snapshot(hotels_reviews_snapshot_parsed, hotel_id)
    singer.write_record('hotel_reviews_snapshot', snapshot)
    start_date = int(snapshot.get('snapshot_start_date', 0))
    end_date = int(snapshot.get('snapshot_end_date', 0))
    hotel_reviews_snapshot_url = str(snapshot.get('hotel_reviews_snapshot_url', ''))
    for site in hotels_reviews_snapshot_parsed['valuesByReviewSite']:
        snapshot_by_site = parse_hotel_reviews_snapshot_by_site(hotel_id, \
            hotel_reviews_snapshot_url, start_date, end_date, site)
        singer.write_record('hotel_reviews_snapshot_by_site', snapshot_by_site)
    for period in hotels_reviews_snapshot_parsed['valuesByTime']:
        snapshot_by_time = parse_hotel_reviews_snapshot_by_time(hotel_id, \
            hotel_reviews_snapshot_url, period)
        singer.write_record('hotel_reviews_snapshot_by_time', snapshot_by_time)

def parse_hotel(hotel):
    # flatten links and get hotel_id
    hotel_url = ''
    hotel_id = 0
    hotel_reviews_snapshot_url = ''
    if 'links' not in hotel:
        links_json = {}
    else:
        links_json = hotel['links']
        for link in hotel['links']:
            if link['rel'] == "self":
                hotel_url = link['href']
                match = re.search(r".*/hotels/(.*)", hotel_url)
                if match:
                    hotel_id = int(match.group(1))
                else:
                    hotel_id = 0
            if link['rel'] == "reviewssnapshot":
                hotel_reviews_snapshot_url = link['href']
    return {
        'hotel_id': int(hotel_id),
        'hotel_url': str(hotel_url),
        'hotel_reviews_snapshot_url': str(hotel_reviews_snapshot_url),
        'hotel_json': str(hotel),
        'name': str(hotel.get('name', '')),
        'slug': str(hotel.get('slug', '')),
        'logo': str(hotel.get('logo', '')),
        'url': str(hotel.get('url', '')),
        'address1': str(hotel.get('address1', '')),
        'address2': str(hotel.get('address2', '')),
        'city': str(hotel.get('city', '')),
        'state': str(hotel.get('state', '')),
        'postal_code': str(hotel.get('postalCode', '')),
        'country': str(hotel.get('country', '')),
        'trip_advisor_id': int(hotel.get('tripAdvisorId', 0)),
        'revinate_purchase_uri': str(hotel.get('revinatePurchaseUri', '')),
        'revinate_login_uri': str(hotel.get('revinateLoginUri', '')),
        'account_type': str(hotel.get('revinatePurchaseUri', '')),
        'links_json': str(links_json)
    }

def fetch_hotels(headers, params):
    url = '{}/hotels'.format(BASE_URL)
    resp = request(url, headers, params)
    parsed = json.loads(resp.text)
    return parsed

def sync_hotels(headers):
    page = 0 # initialize at first page
    rec = 1 # initialize first record
    total_pages = 1 # initial total pages, which gets overwritten
    total_elements = 0 # initial total elements, which gets overwritten
    size = 10 # number of records per request
    # loop thru all pages
    while (page + 1) <= total_pages:
        if (rec + size) <= total_elements:
            rec_to = rec + size - 1
        else:
            rec_to = total_elements
        LOGGER.info('Page {} of {} Total Pages, Record {}-{} of {} Total Records'.format( \
            str(page + 1), str(total_pages), str(rec), str(rec_to), str(total_elements)))
        params = {
            'page': page,
            'size': size,
            'sort': 'id,ASC'
        }
        try:
            hotels_parsed = fetch_hotels(headers, params)
        except Exception as exception:
            LOGGER.exception(exception)
            break
        # loop thru all records on page
        for record in hotels_parsed['content']:
            parsed_hotel = parse_hotel(record)
            singer.write_record('hotels', parsed_hotel)
            hotel_id = str(parsed_hotel.get('hotel_id', ''))
            sync_hotel_reviews_snapshot(headers, hotel_id)
            rec = rec + 1
        page_json = hotels_parsed['page']
        total_pages = int(page_json.get('totalPages', 1))
        total_elements = int(page_json.get('totalElements', 0))
        page = page + 1
    LOGGER.info("Done syncing hotels.")

def generate_hash_key(username, api_secret, unix_timestamp):
    user_time = username + str(unix_timestamp)
    user_time_enc = user_time.encode()
    api_secret_enc = api_secret.encode()
    dig = hmac.new(api_secret_enc, user_time_enc, digestmod=hashlib.sha256).digest()
    dig_hex = binascii.hexlify(dig)
    hash_key = repr(dig_hex)[2:(len(repr(dig_hex))-1)]
    LOGGER.info("Generated user-time hash key.")
    return hash_key

def do_sync(args):
    LOGGER.info("Starting sync.")
    CONFIG.update(args.config)
    if args.state:
        STATE.update(args.state)
    # Get current timestamp - 5 min
    minutes = 5
    unix_timestamp = int(time.time())-(60 * minutes)
    hash_key = generate_hash_key(
        username=CONFIG.get('username'),
        api_secret=CONFIG.get('api_secret'),
        unix_timestamp=unix_timestamp
    )
    headers = {
        'X-Revinate-Porter-Username': CONFIG.get('username'),
        'X-Revinate-Porter-Timestamp': str(unix_timestamp),
        'X-Revinate-Porter-Key': CONFIG.get('api_key'),
        'X-Revinate-Porter-Encoded': hash_key
    }
    singer.write_schema('hotels',
                        schemas.hotels,
                        key_properties=['hotel_id'])
    singer.write_schema('reviews',
                        schemas.reviews,
                        key_properties=['review_id'])
    singer.write_schema('hotel_reviews_snapshot',
                        schemas.hotel_reviews_snapshot,
                        key_properties=['hotel_id', 'snapshot_start_date'])
    singer.write_schema('hotel_reviews_snapshot_by_site',
                        schemas.hotel_reviews_snapshot_by_site,
                        key_properties=['hotel_id', 'review_site_id', 'snapshot_start_date'])
    singer.write_schema('hotel_reviews_snapshot_by_time',
                        schemas.hotel_reviews_snapshot_by_time,
                        key_properties=['hotel_id', 'unix_time'])
    sync_hotels(headers)
    sync_reviews(headers, CONFIG, STATE)

def main_impl():
    args = utils.parse_args(REQUIRED_CONFIG_KEYS)
    try:
        do_sync(args)
    except RuntimeError:
        LOGGER.fatal("Run failed.")
        exit(1)

@utils.handle_top_exception(LOGGER)
def main():
    try:
        main_impl()
    except Exception as exc:
        LOGGER.critical(exc)
        raise exc

if __name__ == '__main__':
    main()
