from flask import Flask, render_template, redirect, request, flash, jsonify
from flask.ext.socketio import SocketIO, emit
import model
import json
import datetime
import time
from threading import Thread
import requests

app = Flask(__name__)
app.secret_key = 'secret_key' # TODO: change/ figure out if client knows about this
socketio = SocketIO(app)
thread = None

def background_thread():
    count = 0
    while True:
        time.sleep(10) # reports come every 65-69 sec- change to 65
        count += 1
        new_earthquake = handle_new_quake_json()

        socketio.emit("new_earthquake", new_earthquake)

        reformatted_new_earthquake = reformat_new_quake_json(new_earthquake)
        if reformatted_new_earthquake:
            write_new_quakes_to_db(new_earthquake)

@app.route('/')
def index():
    global thread
    if thread is None:
        thread = Thread(target=background_thread)
        thread.start()
    return render_template("index.html")

@socketio.on("new_earthquake") #TODO do I need this line?
@app.route("/new_earthquake")
def handle_new_quake_json():
    r = requests.get("http://earthquake.usgs.gov/earthquakes/feed/geojson/2.5/day")
    new_earthquake = r.json()
    return new_earthquake

# TODO: refactor- this needs persist across app's running
last_update = "1404691200" # need to reseed DB just before deploy? may not need to strip ms from below vars- 
# get last_update from db... when was last time run
recorded_min_magnitude = 6.5 # TODO using DB with data of 2.5+ quakes- consider how to draw these (MANY MORE POINTS)

@app.route("/reformat_new_quake_json")
def reformat_new_quake_json(update):
    update_release_time = str(update["metadata"]["generated"])[:-3] # take off ms
    update_release_time = int(update_release_time)
    global last_update
    print "first update %s" % last_update
    last_update = update_release_time 
    print "updated last_update %s" % last_update
    new_quake_dict = {}

    if update_release_time > last_update:
        for quake in update["features"]:
            props = quake["properties"]
            quake_id = quake["id"]

            quake_time = int(props["time"][:-3])  # take off ms
            formatted_quake_time = datetime.datetime.fromtimestamp(quake_time)
            quake_year = formatted_quake_time.strftime("%Y")
            quake_month = formatted_quake_time.strftime("%m")
            quake_day = formatted_quake_time.strftime("%d")
            
            quake_updated = props["updated"][:-3] # take off ms
            quake_magnitude = props["mag"]

            # are following conditions sufficient?
            if quake_updated > last_update and quake_magnitude >= recorded_min_magnitude:
                quake_magnitude_type = props["magnitudeType"]
                quake_tsunami = props["tsunami"]
                quake_latitude = quake["geometry"]["coordinates"][1]
                quake_longitude = quake["geometry"]["coordinates"][0] 
        
                new_quake_dict[quake_id] = {"updated":quake_updated, "year":quake_year, "month":quake_month, "day":quake_day,
                    "magnitude":quake_magnitude, "mag_type":quake_magnitude_type, "tsunami":quake_tsunami, 
                    "longitude":quake_longitude, "latitude":quake_latitude}
        print new_quake_dict
        return new_quake_dict

@app.route("/write_new_quakes_to_db")
def write_new_quakes_to_db(new_quake_dict):
    print "writing to db"
    db = json.loads(read_quakes_from_db())
    if new_quake_dict["id"] in db:
        pass
        # update
    else:
        # magnitude = new_quake_dict["magnitude"]
        # magnitude_type = new_quake_dict["magnitude_type"].split("_")[0].lower()

        new_quake = model.Quake(
            tsunami = new_quake_dict["tsunami"],
            year = new_quake_dict["year"],
            month = new_quake_dict["month"],
            day = new_quake_dict["day"],
            magnitude = new_quake_dict["magnitude"],
            # magnitude_mw = magnitude if magnitude_type == "mw",
            # magnitude_ms = magnitude if magnitude_type == "ms",
            # magnitude_mb = magnitude if magnitude_type == "mb",
            # magnitude_ml = magnitude if magnitude_type == "ml" or magnitude_type == "md", # these are consistent
            # magnitude_mfa = magnitude if magnitude_type == "mfa",
            # magnitude_unk = magnitude if magnitude_type == "unk",
            latitude = new_quake_dict["latitude"],
            longitude = new_quake_dict["longitude"]
        )
    model.session.add(new_quake)
    model.session.commit()

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