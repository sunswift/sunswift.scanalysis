#!/bin/sh

wget --mirror --user=sunswift --password=scanalysis -r http://clients.theweather.com.au/sunswift/data
mv clients.theweather.com.au/sunswift weatherdata
rm -r clients.theweather.com.au
rm weatherdata/index.html*
rm weatherdata/data/index.html*
rm -r ../../data/weather/theweather
mv weatherdata ../../data/weather/theweather