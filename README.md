pyspotprice
===========

A simple script to check kitco for current metal spot price values and determine the value of your metal holdings.


## Setup

    git clone git@github.com:samdolan/pyspotprice.git
    mkvirtualenv pyspotprice
    pip install -r requirements.txt
    chmod a+x pyspotprice.py
    python pyspotprice.py --help
    
    
> (pyspotprice) $ python pyspotprice.py --help
> usage: pyspotprice.py [-h] [-i] [-u] [-p] [-a] [-c]

> optional arguments:
>  -h, --help       show this help message and exit
>  -i, --inventory  Print out the current portfolio inventory
>  -u, --update     Update your portfolio
>  -p, --prices     Print out the current market prices
>  -a, --all        Print out the current prices and the market value of the
                   portfolio
>  -c, --clear      Clear out the data store and set the default values.


By default the script runs the --all flag that looks at your local inventory portfolio and checks it against the live prices.
