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
app.debug = True
socketio = SocketIO(app)
thread = None

# TODO: refactor- this needs persist across app's running
last_update = "1406001828000" # need to reseed DB just before deploy? may not need to strip ms from below vars- 
# In gen, get last_update from db... when was last time run
min_recorded_magnitude = 6

def background_thread():
    count = 0
    while True:
        time.sleep(30) # reports come every 65-69 sec- change to 65
        count += 1
        new_earthquake = handle_new_quake_json()
        socketio.emit("new_earthquake", new_earthquake)
        # draw new points
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

# refactor this and reformat_new_quake_json to deal w both reading from db and handling new json
@app.route("/new_earthquake")
def handle_new_quake_json():
    r = requests.get("http://earthquake.usgs.gov/earthquakes/feed/geojson/2.5/week")
    new_quakes = r.json()
    global update_release_time
    update_release_time = int(new_quakes["metadata"]["generated"])
    global last_update
    print "first update %s" % last_update
    last_update = update_release_time 
    print "updated last_update %s" % last_update

    new_quake_dict = {}

    for quake in new_quakes["features"]:
        props = quake["properties"]
        quake_updated = props["updated"]
        quake_magnitude = props["mag"]
        quake_id = quake["id"]
        quake_time = props["time"]
        quake_tsunami = props["tsunami"]
        quake_latitude = quake["geometry"]["coordinates"][1]
        quake_longitude = quake["geometry"]["coordinates"][0] 

        new_quake_dict[quake_id] = {"timestamp":quake_time, "updated":quake_updated,
            "magnitude":quake_magnitude, "tsunami":quake_tsunami, 
            "longitude":quake_longitude, "latitude":quake_latitude, "id": quake_id}

            # array of dictionaries
            # and filter out no lat/long/magnitude
    return json.dumps(new_quake_dict)

@app.route("/reformat_new_quake_json")
def reformat_new_quake_json(update):
    update = json.loads(update)
    new_quake_dict = {}

    if update_release_time > last_update:
        for quake in update["features"]:
            props = quake["properties"]
            quake_updated = props["updated"]
            quake_magnitude = props["mag"]

            # are following conditions sufficient?
            if quake_updated > last_update and quake_magnitude >= min_recorded_magnitude:
                quake_id = quake["id"]
                quake_time = props["time"]
                quake_tsunami = props["tsunami"]
                quake_latitude = quake["geometry"]["coordinates"][1]
                quake_longitude = quake["geometry"]["coordinates"][0] 
        
                new_quake_dict[quake_id] = {"timestamp":quake_time, "updated":quake_updated,
                    "magnitude":quake_magnitude, "tsunami":quake_tsunami, 
                    "longitude":quake_longitude, "latitude":quake_latitude, "id": quake_id}
    return new_quake_dict

@app.route("/write_new_quakes_to_db")
def write_new_quakes_to_db(new_quake_dict):
    # filter out new quakes above M6 here, not in reformat, then can del reformat
    print "writing to db"
    db = json.loads(read_quakes_from_db()) # inefficient to read from db every time? - how to get around- perhaps memcached
    print db
    for quake in new_quake_dict:
        if quake in db:
            print "updating quake"
            existing_quake = model.Quake.query.get(quake) # id
            existing_quake.timestamp = quake["timestamp"]
            existing_quake.updated = quake["updated"]
            existing_quake.magnitude = quake["magnitude"]
            existing_quake.tsunami = quake["tsunami"]
            existing_quake.longitude = quake["longitude"]
            existing_quake.latitude = quake["latitude"]
        else:
            print "adding new quake"
            new_quake = model.Quake(
                id = new_quake_dict["id"],
                tsunami = new_quake_dict["tsunami"],
                timestamp = new_quake_dict["timestamp"],
                updated = new_quake_dict["updated"],
                magnitude = new_quake_dict["magnitude"],
                latitude = new_quake_dict["latitude"],
                longitude = new_quake_dict["longitude"]
            )
        model.session.add(new_quake)
    model.session.commit()

    quake_time = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=(quake.timestamp/1000)) # converted from milliseconds to seconds
    quake_year = quake_time.strftime("%Y")
    response_dict = {quake_year: {"id": quake.id, "timestamp": quake.timestamp,
                "latitude": quake.latitude, "longitude": quake.longitude,
                "magnitude": quake.magnitude, "tsunami": quake.tsunami}}
    return response_dict

@app.route("/read_quakes_from_db")
def read_quakes_from_db():
    historical_quake_data = model.session.query(model.Quake).all()
    response_dict = {}
    
    for quake in historical_quake_data:
        quake_time = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=(quake.timestamp/1000)) # converted from milliseconds to seconds
        quake_year = quake_time.strftime("%Y")
        response_dict.setdefault(quake_year, []).append({
                "id": quake.id, "timestamp": quake.timestamp,
                "latitude": quake.latitude, "longitude": quake.longitude,
                "magnitude": quake.magnitude, "tsunami": quake.tsunami})
    return json.dumps(response_dict)
    
if __name__ == "__main__":
    socketio.run(app)