from flask import Flask, render_template, redirect, request, flash, jsonify, session
from flask.ext.socketio import SocketIO, emit
import model
import json
from datetime import date
import time
from threading import Thread
import requests

app = Flask(__name__)
app.secret_key = 'secret_key' # change
socketio = SocketIO(app)
thread = None

# sleep 10 sec, make request, broadcast response only if new earthquakes published (saves bandwidth)
def background_thread():
    count = 0
    while True:
        time.sleep(10)
        count += 1
        new_earthquake = handle_new_quake_json()
        socketio.emit("new_earthquake", new_earthquake) # this is broadcast to mult browsers

        write_new_quakes_to_db()
        # user_id = b_session['user']
        # last_quake_seen = b_session['user']['last']

@app.route('/')
def index():
    global thread
    if thread is None:
        thread = Thread(target=background_thread)
        thread.start()
    return render_template("index.html")

@socketio.on("new earthquake")
def handle_new_quake_json():
    r = requests.get("http://earthquake.usgs.gov/earthquakes/feed/geojson/2.5/day")
    new_earthquake = r.json()
    return json.dumps(new_earthquake)

# keep in memory instead of loading from DB everytime (Redis?)
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
        
            if quake.year in response_dict:
                response_dict[quake.year].append({"id": quake.id, 
                    "latitude": quake.latitude, "longitude": quake.longitude,
                    "year": quake.year, "month": quake.month, "day": quake.day, "hour": quake.hour, 
                    "magnitude": avg_magnitude})
            else:
                response_dict[quake.year] = [{"id": quake.id, 
                    "latitude": quake.latitude, "longitude": quake.longitude,
                    "year": quake.year, "month": quake.month, "day": quake.day, "hour": quake.hour, 
                    "magnitude": avg_magnitude}]

    return json.dumps(response_dict)

@app.route("/write_new_quakes_to_db")
def write_new_quakes_to_db():
    last_update = ""
    update = json.loads(handle_new_quake_json())
    for key, value in update.iteritems():
        if key == "features":
            counter = 0
            while counter < len(update[key]):
                quake_time = update[key][counter]["properties"]["time"]
                if quake_time > last_update:
                    pass
                counter += 1
       
            # convert quake epoch time to sep mo, day, yr, etc
            # new_quake = model.Quake(
            #     tsunami = 
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
            #     latitude = 
            #     longitude = 
            # )
        # model.session.add(new_quake)
        # model.session.commit()
        last_update = time.time() # better to get from metadata in json


if __name__ == "__main__":
    socketio.run(app)