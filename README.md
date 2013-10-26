pyspotprice
===========

A simple script to check kitco for current metal spot price values and determine the value of your metal holdings.

Using this script you can create a local inventory of how many ounces of silver, gold, and platinum you have and use 
that to query the live price data to see what the current value of your holdings are.

## Setup

    git clone git@github.com:samdolan/pyspotprice.git
    cd pyspotprice
    mkvirtualenv pyspotprice
    pip install -r requirements.txt
    chmod +x pyspotprice.py
    ./pyspotprice.py --help
    
    
### Available options   
     (pyspotprice) $ python pyspotprice.py --help
      usage: pyspotprice.py [-h] [-i] [-u] [-p] [-a] [-c]

     optional arguments:
      -h, --help       show this help message and exit
      -i, --inventory  Print out the current portfolio inventory
      -u, --update     Update your portfolio
      -p, --prices     Print out the current market prices
      -a, --all        Print out the current prices and the market value of the
                   portfolio
      -c, --clear      Clear out the data store and set the default values.


By default the script runs the --all flag that looks at your local inventory portfolio and checks it against the live prices.

### Example usage

    (pyspotprice) $ ./pyspotprice.py --update
    ---- Existing inventory   ---------------------------------------------------------
    +----------+----------+
    | Metal    | Quantity |
    +----------+----------+
    | platinum |        0 |
    | silver   |        0 |
    | gold     |        0 |
    +----------+----------+
    ---- Update inventory   -----------------------------------------------------------
    Platinum => 0
    Silver => 1
    Gold => 2
    Which ID would you like to update? 0
    What is the new value in ounces? 2
    Saved!
    ---- Updated inventory   ----------------------------------------------------------
    +----------+----------+
    | Metal    | Quantity |
    +----------+----------+
    | platinum |      2.0 |
    | silver   |        0 |
    | gold     |        0 |
    +----------+----------+

    (pyspotprice) $ ./pyspotprice.py --update
    ---- Existing inventory   ---------------------------------------------------------
    +----------+----------+
    | Metal    | Quantity |
    +----------+----------+
    | platinum |      2.0 |
    | silver   |        0 |
    | gold     |        0 |
    +----------+----------+
    ---- Update inventory   -----------------------------------------------------------
    Platinum => 0
    Silver => 1
    Gold => 2
    Which ID would you like to update? 2
    What is the new value in ounces? 35
    Saved!
    ---- Updated inventory   ----------------------------------------------------------
    +----------+----------+
    | Metal    | Quantity |
    +----------+----------+
    | platinum |      2.0 |
    | silver   |        0 |
    | gold     |     35.0 |
    +----------+----------+

    (pyspotprice) $ ./pyspotprice.py --prices
    ---- Current prices   -------------------------------------------------------------
    Downloading page....
    Finished download.
    +----------+------------+------------+--------+--------+--------------+----------+
    | Metal    |    Date    | Time (EST) |    Bid |    Ask | Change (USD) | Change % |
    +----------+------------+------------+--------+--------+--------------+----------+
    | Platinum | 10/25/2013 | 17:04      | 1451.0 | 1461.0 |          5.0 |     0.35 |
    | Silver   | 10/25/2013 | 17:14      |   22.6 |   22.7 |        -0.13 |    -0.55 |
    | Gold     | 10/25/2013 | 17:14      | 1352.9 | 1353.9 |          5.6 |     0.42 |
    +----------+------------+------------+--------+--------+--------------+----------+

    (pyspotprice) $ ./pyspotprice.py
    Downloading page....
    Finished download.
    +----------+----------+--------+----------+
    | Metal    | Quantity |    Ask |    Total |
    +----------+----------+--------+----------+
    | Platinum |      2.0 | 1461.0 |   2922.0 |
    | Silver   |        0 |   22.7 |      0.0 |
    | Gold     |     35.0 | 1353.9 |  47386.5 |
    |          |          |  Total | $50308.5 |
    +----------+----------+--------+----------+
