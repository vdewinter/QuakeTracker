QuakeTracker
============
![alt tag] (https://github.com/vdewinter/QuakeTracker/blob/master/QuakeTracker.png)

QuakeTracker is an interactive visualization of earthquakes magnitude 3 or greater from the past week and all earthquakes of magnitude 6 or greater since 1900 colored and sized by magnitude. This app maintains a websocket connection between the client and backend, which requests GeoJSON reports of the last week of earthquakes every minute from USGS. Thanks to D3's enter, append, exit/remove model, new earthquakes are added to the map dynamically when the backend emits new data from the reports, and earthquakes older than one week (no longer in the reports) are removed from the set of recent quakes and added to historical quakes.


Click on the labeled circles to filter recent or historical earthquakes by magnitude. Filters are grayed out when no earthquakes of a certain magnitude are present in the recent quakes data. Use the slider to display quakes since 1900 by year. Hover over any map point for information about an earthquake's magnitude and when it occurred.
