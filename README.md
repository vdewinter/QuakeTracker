QuakeTracker
============
![alt tag] (https://github.com/vdewinter/QuakeTracker/blob/master/QuakeTracker.png)

QuakeTracker is an interactive visualization of earthquakes magnitude 3 or greater from the past week and all earthquakes of magnitude 6 or greater since 1900 colored and sized by magnitude. The application's Python backend requests GeoJSON reports of the last week of earthquakes from the US Geological Survey in real-time. 


QuakeTracker uses a websocket connection between the client and backend in order to limit the number of requests to USGS' server. When the backend emits new data to the client, new points are added to the map, and earthquakes older than one week (no longer in the reports) are removed. Recent earthquakes of magnitude 6 or greater are added to the database of historical quakes. These dynamic updates are accomplished by D3.js's enter, append, exit/remove model, which binds data dynamically to DOM elements upon each new earthquake report. D3's transition, duration, and ease methods are used for animating the circles.


To filter recent or historical earthquakes by magnitude, click on the labeled circles. Filters are grayed out when no earthquakes of a certain magnitude are present in the recent quakes data. The filter circles reactivate when a new relevant earthquake is reported. Use the slider to display quakes since 1900 by year. Hover over any map point for information about an earthquake's magnitude and when it occurred.
