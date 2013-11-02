#!/usr/bin/env python

from __future__ import print_function
from bs4 import BeautifulSoup
from prettytable import PrettyTable
import requests
import os
import argparse
import json
import datetime
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
        self.date = str(get_cell_value(info_cells[4]))

        # The time of the data was created
        self.time_est = str(get_cell_value(info_cells[5]))
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
            return self.get_default_map()
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

        Caller is responsible for calling our save method to persist the changes
        to disk.

        :param metal_type: A metal type in ALL_METALS
        :param quantity: An int or float with the quantity.
        """
        add = False
        if quantity.startswith('+'):
            quantity = quantity.replace('+', '')
            add = True

        subtract = False
        if quantity.startswith('-'):
            quantity = quantity.replace('-', '')
            subtract = True

        try:
            quantity = float(quantity)
        except ValueError:
            raise

        new_quantity = self.get_quantity(metal_type)
        if add:
            new_quantity += quantity
        elif subtract:
            new_quantity -= quantity
        else:
            new_quantity = quantity

        if new_quantity < 0:
            new_quantity = 0

        self.inventory_map[metal_type] = new_quantity

    def get_quantity(self, metal_type):
        """Get the current quantity for the passed in metal_type.

        :param metal_type: The metal type from ALL_METALS
        :returns: The current quantity of the metal in our database.
        """
        return self.inventory_map.get(metal_type, 0)


def get_content(url):
    """Get the content from the specified url.

    If there is an exception we'll retry until the user cancels.
    """
    print('Downloading page....')

    try:
        resp = requests.get(URL)
    except Exception as e:
        retry_secs = 15
        print("Got exception fetching content. Sleeping for {} secs. {}".format(
            retry_secs, e
        ))
        time.sleep(retry_secs)
        return get_content(url)

    print('Finished download.')
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

    cols = ("Metal", "Date", "Time (EST)", "Bid",
            "Ask", "Change (USD)", "Change %")
    table = PrettyTable(cols, title="Current Prices")
    table.align['Metal'] = 'l'
    table.align['Time (EST)'] = 'l'
    table.align['Bid'] = 'r'
    table.align['Ask'] = 'r'
    table.align['Change (USD)'] = 'r'
    table.align['Change %'] = 'r'

    for k, spot_info in prices_dict.items():
        row = (
            k.capitalize(), spot_info.date, spot_info.time_est,
            spot_info.bid, spot_info.ask,
            spot_info.change_usd, spot_info.change_percent,
        )
        table.add_row(row)

    print(table)

    return prices_dict


def print_inventory():
    """Print out our local metal inventory"""
    inventory = InventoryStore()

    cols = ("Metal", "Quantity")
    table = PrettyTable(cols, title="Current Inventory")
    table.align['Metal'] = 'l'
    table.align['Quantity'] = 'r'

    for metal_type, quantity in inventory.inventory_map.items():
        table.add_row((metal_type, quantity))

    print(table)

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
        current_value = inventory.get_quantity(name)
        print("{0} | Current Quantity: {1}".format(name.capitalize(), current_value))

        new_value = raw_input('New value (exact value or +/- offset or empty to keep the current value): ')

        # if nothing was entered, keep the existing value
        if new_value == '':
            continue

        inventory.set_quantity(name, new_value)

    inventory.save()

    print("Saved!")

    return inventory


def print_inventory_values(prices_dict=None, inventory=None):
    """Print the value of our local inventory store off the live market.

    :param prices_dict: The dictionary mapping of metal types to SpotPrice
        objects. If not passed in, we do the lookup on the site automatically.

    :param inventory: The local ```InventoryStore``` object.
    """
    prices_dict = prices_dict or get_prices_dict()
    inventory = inventory or InventoryStore()

    rows = ('Metal', 'Quantity', 'Ask', 'Total')
    table = PrettyTable(rows, title="Current inventory values")

    table.align['Metal'] = 'l'
    table.align['Quantity'] = 'r'
    table.align['Ask'] = 'r'
    table.align['Total'] = 'r'

    total_cents = 0
    for metal_type, quantity in inventory.inventory_map.items():
        # Get the price info for this metal
        spot_info = prices_dict[metal_type]

        # How much do we have?
        metal_inventory = inventory.inventory_map[metal_type]

        # What's the total worth?
        total_metal_cents = spot_info.ask_cents * metal_inventory

        # Increase our running total to display later
        total_cents += total_metal_cents

        table.add_row((metal_type.capitalize(),
                       metal_inventory,
                       spot_info.ask,
                       total_metal_cents / 100.0))

    table.add_row(('', '',
                   'Total', '${}'.format(total_cents / 100.0)))

    print(table)


def _print_header(header_text):
    """Helper method to display a header for the various sections"""
    line_length = 80
    print('-' * 4, header_text, ' ', \
          (line_length - len(header_text) - 5) * '-')


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

    print(datetime.datetime.now())

    if args.inventory:
        print_inventory()

    elif args.update:
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
            print('Clearing cancelled.')
            return
        else:
            _print_header('Clearing store')
            inventory = InventoryStore()
            inventory.clear()
            print('Cleared.')

    # Default should be print the inventory and current prices
    else:
        print_inventory_values()


if __name__ == '__main__':
    main()


