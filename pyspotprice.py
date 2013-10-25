#!/usr/bin/env python

from bs4 import BeautifulSoup
import requests
import os
import argparse
import json
import time

# Misc. constants
URL = 'http://www.kitco.com/market/'
INVENTORY_FILE_PATH = os.path.expanduser('~/.pyspotprice.json')

# Keys for the various metals we're interested in
GOLD_KEY = 'gold'
SILVER_KEY = 'silver'
PLATINUM_KEY = 'platinum'

ALL_METALS = (GOLD_KEY, SILVER_KEY, PLATINUM_KEY)


class SpotInfo(object):
    """Helper object for storing all of the spot data for a particular metal

    :param metal_type: A key in ```ALL_METALS```
    :param info_cells: A list of bs4 "td" soup objects.
    """
    def __init__(self, metal_type, info_cells):
        self.metal_type = metal_type

        # here just for debugging
        self.info_cells = info_cells

        # The date string the data was created in "%m/%d/%Y" format
        self.date = get_cell_value(info_cells[4])

        # The time of the data was created
        self.time_est = get_cell_value(info_cells[5])
        self.bid_cents = \
            self._convert_usd_string_cents(get_cell_value(info_cells[6]))
        self.ask_cents = \
            self._convert_usd_string_cents(get_cell_value(info_cells[7]))
        self.change_usd_cents = \
            self._convert_usd_string_cents(get_cell_value(info_cells[8]))

        self.change_percent = \
            float(get_cell_value(info_cells[9]).replace('%', ''))

    def _convert_usd_string_cents(self, usd_string):
        """Convert a string of dollars to cents for easier calculations.

        :returns: An int of the dollar string (e.g. "$23.43") in cents.
            If conversion fails, a default string.
        """
        try:
            return int(usd_string.replace('.', ''))
        except ValueError:
            return 'N/A'

    @property
    def bid(self):
        """Get the bid price in a dollar float"""
        return self.bid_cents / 100.0 if self.bid_cents else '-'

    @property
    def ask(self):
        """Get the ask price in a dollar float"""
        return self.ask_cents / 100.0 if self.ask_cents else '-'

    @property
    def change_usd(self):
        """Get the change from previous days in a dollar offset"""
        return self.change_usd_cents / 100.0 if self.change_usd_cents else '-'


class InventoryStore(object):
    """Object to store the user's current inventory of metals"""

    def __init__(self):
        self.inventory_map = self.get_inventory_map()

    def get_default_map(self):
        """Get a default map that we should start with

        Starts with a dictionary of all of the metals we care about at 0"""
        return dict((metal_type_key, 0) for metal_type_key in ALL_METALS)

    def get_inventory_map(self):
        """Get the dictionary mapping of our inventory

        If the storage file does not exist, then a blank default dict will be
        returned.
        """
        if not os.path.exists(INVENTORY_FILE_PATH):
            return self.get_default_dict()
        with open(INVENTORY_FILE_PATH, 'r') as f:
            return json.loads(f.read())

    def save(self):
        """Save our inventory_map to the path defined in INVENTORY_FILE_PATH"""
        with open(INVENTORY_FILE_PATH, 'w+') as f:
            f.write(json.dumps(self.inventory_map))

    def clear(self):
        """Clear out the store and reset to the default values."""
        self.inventory_map = self.get_default_map()
        self.save()

    def set_quantity(self, metal_type, quantity):
        """Helper method to set a metal_types' quantity.

        You are responsible for calling our save method to persist the changes
        to disk.

        TODO: Add support for offsets. For example: a string of "+10" increase
        the quantity by 10

        :param metal_types: A metal type in ALL_METALS
        :param quantity: An int or float with the quantity.
        """
        assert isinstance(quantity, (int, float)), \
                "quantity must be an int or float. Got: {}".format(quantity)

        self.inventory_map[metal_type] = quantity


def get_content(url):
    """Get the content from the specified url.

    If there is
    """
    print 'Downloading page....'


    try:
        resp = requests.get(URL)
    except Exception as e:
        retry_secs = 15
        print "Got exception fetching content. Sleeping for {} secs. {}".format(
                retry_secs, e
        )
        time.sleep(retry_secs)
        return get_content(url)


    print 'Finished download.'
    return resp.content


def get_cell_value(cell):
    """Helper method to get the value of a cell inside the kitco spot price
    info table."""
    p = cell.find('p')

    # The percentage change and dollar change are wrapped in <p> tags
    if p:
        return p.contents[0]
    else:
        return cell.contents[0]


def parse_prices(content):
    """Parse the html content and extract the price data for our metals.

    :param content: The raw HTML content of the page.

    :returns: A mapping of metal_name => SpotInfo instances.
    """

    soup = BeautifulSoup(content)

    spot_info = {}

    for metal in ALL_METALS:
        # The New York spot price is the first table and the metal name is
        # uppercase
        val_cell = soup.findAll('a', text=metal.upper())[0]

        # All the info we need is the row that contains the metal name
        val_row = val_cell.findParent('tr')

        # Each individual cell has various information about that metal
        cells = val_row.findAll('td')

        spot_info[metal] = SpotInfo(metal, cells)

    return spot_info



def get_prices_dict():
    """Download and parse the page."""
    content = get_content(URL)
    prices_dict = parse_prices(content)
    return prices_dict


def print_prices(prices_dict=None):
    """Print out a table of all of the current prices and changes."""
    prices_dict = prices_dict or get_prices_dict()

    print "Metal | Date | Time (EST) | Bid | Ask | Change (USD) | Change %"
    for k, spot_info in prices_dict.items():
        print u"{} | {} | {} | ${} | ${} | {}%".format(
            k.capitalize(), spot_info.date, spot_info.time_est,
            spot_info.bid, spot_info.ask,
            spot_info.change_usd, spot_info.change_percent,
        )


def print_inventory():
    """Print out our local metal inventory"""
    inventory = InventoryStore()

    print "Metal | Quantity (oz)"
    for  metal_type, quantity in inventory.inventory_map.items():
        print "{} | {}".format(metal_type, quantity)

    return inventory


def update_inventory():
    """Update the local inventory store with command prompts

    TODO: Support increasing by a + or -value

    :returns: The newly current ```InventoryStore``` object.
    """
    inventory = InventoryStore()

    option_dict = dict((i, k)
            for i, k in enumerate(inventory.inventory_map.iterkeys()))

    for i, name in option_dict.items():
        print "{1} => {0}".format(i, name.capitalize())

    try:
        selected_val = int(raw_input("Which ID would you like to update? "))
        if selected_val > len(option_dict.keys()) - 1:
            print 'Please select a valid value'
            return update_inventory()

        new_val = float(raw_input("What is the new value in ounces? "))
    except ValueError:
        # we messed up, just redisplay the prompts

        print "Please enter an int or float!"
        return update_inventory()

    # Save that bad boy
    inventory.set_quantity(option_dict[selected_val], new_val)
    inventory.save()

    print "Saved!"

    return inventory


def print_inventory_values(prices_dict=None, inventory=None):
    """Print the value of our local inventory store off the live market.

    :param prices_dict: The dictionary mapping of metal types to SpotPrice
        objects. If not passed in, we do the lookup on the site automatically.

    :param inventory: The local ```InventoryStore``` object.
    """
    prices_dict = prices_dict or get_prices_dict()
    inventory = inventory or InventoryStore()

    print 'Metal | Total | Change'
    total_cents = 0
    for metal_type, quantity in inventory.inventory_map.items():
        # Get the price info for this metal
        spot_info = prices_dict[metal_type]

        # How much do we have?
        metal_inventory = inventory.inventory_map[metal_type]

        # What's the total worth?
        total_metal_cents = spot_info.bid_cents * metal_inventory

        # Increase our running total to display later
        total_cents += total_metal_cents

        print '{} | ${} | {}'.format(metal_type.capitalize(), total_metal_cents / 100.0, 0)

    print 'Total: ${}'.format(total_cents / 100.0)


def _print_header(header_text):
    """Helper method to display a header for the various sections"""
    line_length = 80
    print '-' * 4, header_text, ' ',  \
        (line_length - len(header_text) - 5) * '-'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--inventory", action="store_true",
            help="Print out the current portfolio inventory")

    parser.add_argument("-u", "--update", action="store_true",
            help="Update your portfolio")

    parser.add_argument("-p", "--prices", action="store_true",
            help="Print out the current market prices")

    parser.add_argument("-a", "--all", action="store_true",
            help="Print out the current prices and the market value of the portfolio")

    parser.add_argument("-c", "--clear", action="store_true",
            help="Clear out the data store and set the default values.")


    args = parser.parse_args()

    print

    if args.inventory:
        _print_header('Current inventory')
        print_inventory()

    elif args.update:
        _print_header('Existing inventory')
        print_inventory()

        _print_header('Update inventory')
        update_inventory()

        _print_header('Updated inventory')
        print_inventory()

    elif args.prices:
        _print_header('Current prices')
        print_prices()

    elif args.clear:
        answer = raw_input("Are you sure you want to clear your data store? "
                "If so type 'yes': ")
        if answer != 'yes':
            print 'Clearing cancelled.'
            return
        else:
            _print_header('Clearing store')
            inventory = InventoryStore()
            inventory.clear()
            print 'Cleared.'

    # Default should be print the inventory and current prices
    else:
        _print_header('Existing inventory')
        inventory = print_inventory()

        _print_header('Current prices')
        prices_dict = print_prices()


        _print_header('Current values')
        print_inventory_values(prices_dict, inventory)


if __name__ == '__main__':
    main()


