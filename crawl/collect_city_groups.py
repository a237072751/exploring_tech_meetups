# -*- coding: utf-8 -*-
#
# Author:   Matt J Williams
#           http://www.mattjw.net
#           mattjw@mattjw.net
# Date:     2015
# License:  MIT License
#           http://opensource.org/licenses/MIT


"""
Collect groups generated by `crawl_groups.py`. Groups are collected according to
their contituent meetups city.
"""


__author__ = "Matt J Williams"
__author_email__ = "mattjw@mattjw.net"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2015 Matt J Williams"


from pprint import pprint
import json
from collections import OrderedDict, defaultdict
import os

import crawl_tools


OUT_DIR = './dat/city_meetup_groups'


def load_group_crawls():
    """
    Load output from `crawl_groups.py`.
    """
    fdir = './dat/groups_crawl'
    country2citycrawls = {}
    for fname in os.listdir(fdir):
        if not fname.endswith('json'):
            continue

        fpath = os.path.join(fdir, fname)
        country = fname.split('.')[0]
        with open(fpath) as f:
            country2citycrawls[country] = json.load(f)
    return country2citycrawls


def discard_duplicates(seq, key_func):
    """
    Discard any duplicates in`seq`. `key_func` is a function that assigns
    an item in `seq` to a key. Order is retained.
    """
    d = OrderedDict()
    for item in seq:
        key = key_func(item)
        if key not in d:
            d[key] = item
    return d.values()


def collect_crawls(country_code, crawls):
    """
    Collect groups into their corresponding (meetup) cities. Removes duplicate
    groups in the same meetup city. Discards any cities that do not belong to
    `country_code`.

    `crawls`: The group crawls for one country. List of dicts. Each dict
    represents a crawl of groups in one geonames location (see
    `crawl_groups.py`).

    Returns:
    Dict that maps from a (meetups) city to a list of groups in that city.
    A meetups city is identified as the string: 'country:state:city'
    """
    # bucketise by meetup city ident
    city2groups = defaultdict(lambda: [])
    for city_crawl in crawls:
        groups_seq = city_crawl['results']
        for group in groups_seq:
            mu_city = group['city']
            mu_state = group.get('state', '')
            mu_country = group['country']
            if mu_country.lower() != country_code.lower():
                continue
            city_ident = '%s:%s:%s' % (mu_country, mu_state, mu_city)
            city2groups[city_ident].append(group)

    # discard duplicates
    for city_ident in city2groups:
        seq = city2groups[city_ident]
        seq = discard_duplicates(seq, lambda item: item['id'])
        city2groups[city_ident] = seq
    
    # sort each city by number of groups
    items = city2groups.items()
    items.sort(key=lambda item: len(item[1]))
    city2groups = OrderedDict(items)
    return city2groups


def main():
    country2citycrawls = load_group_crawls()
    for country_code, citycrawls in country2citycrawls.iteritems():
        city2groups = collect_crawls(country_code, citycrawls)

        for ident, groups in city2groups.iteritems():
            print "%-20s %d" % (ident, len(groups))

        fpath = os.path.join(OUT_DIR, "%s.json" % country_code)
        with open(fpath, 'w') as f:
            json.dump(city2groups, f)
            print
            print "saved to", fpath
            print


if __name__ == "__main__":
    main()
