from flask import Flask, render_template, redirect, request, flash, jsonify
from flask.ext.socketio import SocketIO, emit
import model
import json
from datetime import date
import time
from threading import Thread
import requests

# TODO: consider redis- what is min data needed to show client what it needs-unique id, loc, mag, time

app = Flask(__name__)
app.secret_key = 'secret_key' # TODO: change/ figure out if client knows about this
socketio = SocketIO(app)
thread = None

# sleep, make request, broadcast response only if new earthquakes published (saves bandwidth)
def background_thread():
    count = 0
    while True:
        time.sleep(65) # reports come this often
        count += 1
        new_earthquake = handle_new_quake_json() # TODO this could return dicionary, and then you pass json.dumps(new_earthquake) below
        # call a func here to return data in my format
        reformat_new_quake_json()
        # send to client in correct format
        socketio.emit("new_earthquake", new_earthquake)
        # call write to db
        write_new_quakes_to_db() # TODO take the json data

@app.route('/')
def index():
    global thread
    if thread is None:
        thread = Thread(target=background_thread)
        thread.start()
    return render_template("index.html")

@socketio.on("new earthquake") #TODO find out what this line does
def handle_new_quake_json():
    r = requests.get("http://earthquake.usgs.gov/earthquakes/feed/geojson/2.5/day")
    new_earthquake = r.json()
    return json.dumps(new_earthquake)

@app.route("/read_quakes_from_db")
def read_quakes_from_db():
    date_range = date.today().year - 500
    historical_quake_data = model.session.query(model.Quake).filter(model.Quake.year >= date_range).all()
    response_dict = {}

    for quake in historical_quake_data:
        magnitudes = [quake.magnitude_mw, quake.magnitude_ms, 
        quake.magnitude_mb, quake.magnitude_ml, quake.magnitude_mfa, 
        quake.magnitude_unk]
        magnitudes_to_average = []

        for i in magnitudes:
            if i:
                magnitudes_to_average.append(float(i))
        if len(magnitudes_to_average) > 0:
            avg_magnitude = sum(magnitudes_to_average)/float(len(magnitudes_to_average))
        
            response_dict.setdefault(quake.year, []).append({"id": quake.id, 
                    "latitude": quake.latitude, "longitude": quake.longitude,
                    "year": quake.year, "month": quake.month, "day": quake.day, "hour": quake.hour, 
                    "magnitude": avg_magnitude})
            
    return json.dumps(response_dict)

@app.route("/reformat_new_quake_json")
def reformat_new_quake_json():
    pass

# TODO: refactor- this needs persist across your app's running
last_update = "1404691200" # when project started
recorded_min_magnitude = 6.5 # TODO consider finding DB with data of 2.5+ quakes- consider how to draw these (MANY MORE POINTS)

@app.route("/write_new_quakes_to_db")
def write_new_quakes_to_db():
    update = json.loads(handle_new_quake_json()) # TODO don't call this twice
    update_release_time = update["metadata"]["generated"]

    if update_release_time > last_update:
        for quake in update["features"]:
            props = quake['properties']
            quake_time = props["time"]
            quake_updated = props["updated"]
            quake_magnitude = props["mag"]

            if (quake_time > last_update or quake_updated > last_update) and quake_magnitude >= recorded_min_magnitude:
                quake_magnitude_type = props["magnitudeType"]
                quake_tsunami = props["tsunami"]
                quake_latitude = quake["geometry"]["coordinates"][1]
                quake_longitude = quake["geometry"]["coordinates"][0]

                # add to db (should check if it's in there first?)
                # convert quake epoch time to sep mo, day, yr, etc
                # new_quake = model.Quake(
                #     tsunami = quake_tsunami
                #     year = 
                #     month = 
                #     day = 
                #     hour = 
                #     magnitude_mw = 
                #     magnitude_ms = 
                #     magnitude_mb = 
                #     magnitude_ml = 
                #     magnitude_mfa = 
                #     magnitude_unk = 
                #     latitude = quake_latitude
                #     longitude = quake_longitude
                # )
            # model.session.add(new_quake)
            # model.session.commit()
               
    last_update = update_release_time
    print last_update


if __name__ == "__main__":
    socketio.run(app)