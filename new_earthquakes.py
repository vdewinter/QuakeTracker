import requests

# use request lib
# query url, send json to flask, which will send it to browser

# look at cron (script runs every x period of time)

r = requests.get("http://earthquake.usgs.gov/earthquakes/feed/geojson/2.5/day")
new_earthquake = r.json()

