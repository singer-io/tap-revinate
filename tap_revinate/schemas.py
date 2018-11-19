hotels = {
    'type': ['object', 'null'],
    'properties': {
        'hotel_id': {'type': 'integer'},
        'hotel_url': {'type': 'string'},
        'hotel_reviews_snapshot_url': {'type': 'string'},
        'hotel_json': {'type': 'string'},
        'name': {'type': 'string'},
        'slug': {'type': 'string'},
        'logo': {'type': 'string'},
        'url': {'type': 'string'},
        'address1': {'type': 'string'},
        'address2': {'type': 'string'},
        'city': {'type': 'string'},
        'state': {'type': 'string'},
        'postal_code': {'type': 'string'},
        'country': {'type': 'string'},
        'trip_advisor_id': {'type': 'integer'},
        'revinate_purchase_uri': {'type': 'string'},
        'revinate_login_uri': {'type': 'string'},
        'account_type': {'type': 'string'},
        'links_json': {'type': 'string'}
    }
}

hotel_reviews_snapshot = {
    'type': ['object', 'null'],
    'properties': {
        'hotel_id': {'type': 'integer'},
        'hotel_reviews_snapshot_url': {'type': 'string'},
        'hotel_reviews_snapshot_json': {'type': 'string'},
        'snapshot_start_date': {'type': 'integer'},
        'snapshot_end_date': {'type': 'integer'},
        'aggregate_values_json': {'type': 'string'},
        'aggregate_average_rating': {'type': 'number'},
        'aggregate_new_reviews': {'type': 'number'},
        'aggregate_pos_reviews_pct': {'type': 'number'},
        'aggregate_trip_advisor_market_ranking': {'type': 'integer'},
        'aggregate_trip_advisor_market_ranking_pctl': {'type': 'number'},
        'aggregate_trip_advisor_market_size': {'type': 'integer'},
        'values_by_review_site_json': {'type': 'string'},
        'values_by_time_json': {'type': 'string'},
        'links_json': {'type': 'string'}
    }
}

hotel_reviews_snapshot_by_site = {
    'type': ['object', 'null'],
    'properties': {
        'hotel_id': {'type': 'integer'},
        'hotel_reviews_snapshot_url': {'type': 'string'},
        'site_json': {'type': 'string'},
        'snapshot_start_date': {'type': 'integer'},
        'snapshot_end_date': {'type': 'integer'},
        'review_site_json': {'type': 'string'},
        'review_site_id': {'type': 'integer'},
        'review_site_url': {'type': 'string'},
        'review_site_name': {'type': 'string'},
        'review_site_main_url': {'type': 'string'},
        'review_site_slug': {'type': 'string'},
        'site_average_rating': {'type': 'number'},
        'site_new_reviews': {'type': 'number'},
        'site_pos_reviews_pct': {'type': 'number'},
        'site_trip_advisor_market_ranking': {'type': 'integer'},
        'site_trip_advisor_market_ranking_pctl': {'type': 'number'},
        'site_trip_advisor_market_size': {'type': 'integer'}
    }
}

hotel_reviews_snapshot_by_time = {
    'type': ['object', 'null'],
    'properties': {
        'hotel_id': {'type': 'integer'},
        'hotel_reviews_snapshot_url': {'type': 'string'},
        'time_period_json': {'type': 'string'},
        'unix_time': {'type': 'integer'},
        'snapshot_average_rating': {'type': 'number'},
        'snapshot_new_reviews': {'type': 'number'},
        'snapshot_pos_reviews_pct': {'type': 'number'},
        'snapshot_trip_advisor_market_ranking': {'type': 'integer'},
        'snapshot_trip_advisor_market_ranking_pctl': {'type': 'number'},
        'snapshot_trip_advisor_market_size': {'type': 'integer'}
    }
}

reviews = {
    'type': ['object', 'null'],
    'properties': {
        'review_id': {'type': 'integer'},
        'review_url': {'type': 'string'},
        'review_json': {'type': 'string'},
        'hotel_id': {'type': 'integer'},
        'hotel_url': {'type': 'string'},
        'title': {'type': 'string'},
        'body': {'type': 'string'},
        'author': {'type': 'string'},
        'author_location': {'type': 'string'},
        'date_review': {'type': 'integer'},
        'date_collected': {'type': 'integer'},
        'updated_at': {'type': 'integer'},
        'rating': {'type': 'number'},
        'nps': {'type': 'integer'},
        'review_site_json': {'type': 'string'},
        'review_site_id': {'type': 'integer'},
        'review_site_url': {'type': 'string'},
        'review_site_name': {'type': 'string'},
        'review_site_main_url': {'type': 'string'},
        'review_site_slug': {'type': 'string'},
        'language_json': {'type': 'string'},
        'language_id': {'type': 'integer'},
        'language_url': {'type': 'string'},
        'language_name': {'type': 'string'},
        'language_english_name': {'type': 'string'},
        'language_slug': {'type': 'string'},
        'crawled_url': {'type': 'string'},
        'subratings_json': {'type': 'string'},
        'subratings_cleanliness': {'type': 'number'},
        'subratings_hotel_condition': {'type': 'number'},
        'subratings_rooms': {'type': 'number'},
        'subratings_service': {'type': 'number'},
        'trip_type': {'type': 'string'},
        'guest_stay_json': {'type': 'string'},
        'survey_topics_json': {'type': 'string'},
        'response_json': {'type': 'string'},
        'links_json': {'type': 'string'}
    }
}
