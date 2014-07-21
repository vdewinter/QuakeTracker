from flask import Flask, render_template, redirect, request, flash, jsonify
from flask.ext.socketio import SocketIO, emit
import model
import json
import datetime
import time
from threading import Thread
import requests

# TODO: consider redis- what is min data needed to show client what it needs- timestamp as key, etc
# table with eathquake id, timestamp, json blob -- create index table to query 
# redis puts stuff in memory - have caches- coudl help w page load speed
# TODO: smooth animation- make points grow to full size and then disappear

app = Flask(__name__)
app.secret_key = 'secret_key' # TODO: change/ figure out if client knows about this
socketio = SocketIO(app)
thread = None

# sleep, make request, broadcast/draw points only if new earthquakes published (saves bandwidth)
def background_thread():
    count = 0
    while True:
        time.sleep(10) # reports come every 65-69 sec- change to 65
        count += 1
        new_earthquake = handle_new_quake_json()
        socketio.emit("new_earthquake", new_earthquake)
        reformatted_new_earthquake = reformat_new_quake_json(new_earthquake)
        # display new points on map
        if reformatted_new_earthquake:
            write_new_quakes_to_db(new_earthquake)

@app.route('/')
def index():
    # run once for loading new data on page load unless sleep time is acceptably short
    # new_earthquake = handle_new_quake_json() # returns dict
    # new_earthquake = reformat_new_quake_json(new_earthquake) # returns dict
    # socketio.emit("new_earthquake", new_earthquake)
    # write_new_quakes_to_db(new_earthquake)
    global thread
    if thread is None:
        thread = Thread(target=background_thread)
        thread.start()
    return render_template("index.html")

@socketio.on("new_earthquake") #TODO do I need this line?
def handle_new_quake_json():
    r = requests.get("http://earthquake.usgs.gov/earthquakes/feed/geojson/2.5/day")
    new_earthquake = r.json()
    return new_earthquake

# TODO: refactor- this needs persist across app's running
last_update = "1404691200" # when project started
recorded_min_magnitude = 6.5 # TODO using DB with data of 2.5+ quakes- consider how to draw these (MANY MORE POINTS)

@app.route("/reformat_new_quake_json")
def reformat_new_quake_json(update):
    update_release_time = update["metadata"]["generated"]
    global last_update
    new_quake_dict = {}

    if update_release_time > last_update:
        for quake in update["features"]:
            props = quake['properties']

            quake_time = int(props["time"][:-3]) # take off ms
            formatted_quake_time = datetime.datetime.fromtimestamp(quake_time)
            quake_year = formatted_quake_time.strftime("%Y")
            quake_month = formatted_quake_time.strftime("%m")
            quake_day = formatted_quake_time.strftime("%d")
            
            quake_updated = props["updated"]
            quake_magnitude = props["mag"]

            # are following conditions sufficient? should handle brand new quakes and those with recent updates.
            if quake_updated > last_update and quake_magnitude >= recorded_min_magnitude:
                quake_magnitude_type = props["magnitudeType"]
                quake_tsunami = props["tsunami"]
                quake_latitude = quake["geometry"]["coordinates"][1]
                quake_longitude = quake["geometry"]["coordinates"][0] 
        
                new_quake_dict[quake_time] = {"updated":quake_updated, "year":quake_year, "month":quake_month, "day":quake_day,
                    "magnitude":quake_magnitude, "mag_type":quake_magnitude_type, "tsunami":quake_tsunami, 
                    "longitude":quake_longitude, "latitude":quake_latitude}

                print new_quake_dict

    last_update = update_release_time
    return new_quake_dict

@app.route("/write_new_quakes_to_db")
def write_new_quakes_to_db(new_quake_dict):
    print "writing to db"
    #  if quake already here, update info, else make a new one
    # new_quake = model.Quake(
    #     tsunami = new_quake_dict[quake_tsunami]
    #     year = new_quake_dict[year]
    #     month = new_quake_dict[month]
    #     day = new_quake_dict[day]
    #     magnitude = new_quake_dict[magnitude]
    #     magnitude_type -- handle where to put which type 
    #     latitude = new_quake_dict[quake_latitude]
    #     longitude = new_quake_dict[quake_longitude]
    # )
# model.session.add(new_quake)
# model.session.commit()

@app.route("/read_quakes_from_db")
def read_quakes_from_db():
    date_range = datetime.date.today().year - 500 # only reading data from last 500 years
    historical_quake_data = model.session.query(model.Quake).filter(model.Quake.year >= date_range).all()
    response_dict = {}

    for quake in historical_quake_data:
        magnitudes = [quake.magnitude_mw, quake.magnitude_ms, 
        quake.magnitude_mb, quake.magnitude_ml, quake.magnitude_mfa, 
        quake.magnitude_unk]
        magnitudes_to_average = []

        for i in magnitudes: # only plotting data if magnitude on record
            if i:
                magnitudes_to_average.append(float(i))
        if len(magnitudes_to_average) > 0:
            avg_magnitude = sum(magnitudes_to_average)/float(len(magnitudes_to_average))
        
            response_dict.setdefault(quake.year, []).append({"id": quake.id, 
                    "latitude": quake.latitude, "longitude": quake.longitude,
                    "year": quake.year, "month": quake.month, "day": quake.day, "hour": quake.hour, 
                    "magnitude": avg_magnitude})
            
    return json.dumps(response_dict)
    
if __name__ == "__main__":
    socketio.run(app)