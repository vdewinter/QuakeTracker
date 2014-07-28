from flask import Flask, render_template, redirect, request, flash, jsonify
from flask.ext.socketio import SocketIO, emit
import model
import json
import datetime
import time
from threading import Thread
import requests
import pdb

app = Flask(__name__)
app.secret_key = 'secret_key' # TODO: change
app.debug = True
socketio = SocketIO(app)
thread = None

last_update = 0
ms_per_week = 604800000

def background_thread():
    count = 0
    db_last_update = model.session.query(model.QuakeUpdate).one()
    global last_update 
    last_update = db_last_update.update_time # set to what's in db

    while True:
        time.sleep(60)
        count += 1
        new_earthquake = handle_new_quake_json()
        socketio.emit("new_earthquake", new_earthquake)
        new_earthquake = json.loads(new_earthquake, "latin-1")
        write_new_quakes_to_db(new_earthquake)

@app.route('/')
def index():
    global thread
    if thread is None:
        thread = Thread(target=background_thread)
        thread.start()
    return render_template("index.html")

def create_quake_dict(quake):
    props = quake["properties"]
    quake_updated = props["updated"]
    quake_magnitude = props["mag"]
    quake_id = quake["id"]
    quake_time = props["time"]
    quake_tsunami = props["tsunami"]
    quake_latitude = quake["geometry"]["coordinates"][1]
    quake_longitude = quake["geometry"]["coordinates"][0] 

    return {"id": quake_id, "timestamp":quake_time, "updated":quake_updated,
        "magnitude":quake_magnitude, "tsunami":quake_tsunami, 
        "longitude":quake_longitude, "latitude":quake_latitude}

@socketio.on("new_earthquake")
@app.route("/new_earthquake")
def handle_new_quake_json():
    r = requests.get("http://earthquake.usgs.gov/earthquakes/feed/geojson/2.5/week")
    new_quakes = r.json()

    # when USGS is down - TEST!!!!!!!!!!!!
    if not r.status_code == 200:
        print "USGS down"
        # read all quakes from last week from db
        one_week_ago = int(time.time()) - ms_per_week
        new_quakes = model.session.query(model.Quake).filter(model.Quake.timestamp >= one_week_ago).all()
        
        new_quake_list = []
        for quake in new_quakes:
            new_quake_list.append(quake)
    else:
        global last_update 
        last_update = int(new_quakes["metadata"]["generated"])
        db_last_update = model.session.query(model.QuakeUpdate).one()
        db_last_update.update_time = last_update
        model.session.commit()
        
        new_quake_list = []

        for quake in new_quakes["features"]:
            response = create_quake_dict(quake)
            new_quake_list.append(response)

    return json.dumps(new_quake_list)

def write_new_quakes_to_db(new_quake_dict):
    print "writing to db"
    db = model.session.query(model.Quake).all() # inefficient to read from db every time -> memcached/redis

    db_objects = {}
    for obj in db:
        db_objects[obj.id] = obj

    for quake in new_quake_dict:
        # update quakes that are already in db if they were updated after occurence and update greater than last report time
        global last_update
        quake_update = int(quake["updated"])
        if quake["id"] in db_objects.keys() and ( quake_update > int(quake["timestamp"]) ) and ( quake_update > (last_update - ms_per_week) ):
            print "updating quake"
            existing_quake = model.Quake.query.get(quake["id"])
            existing_quake.timestamp = quake["timestamp"]
            existing_quake.updated = quake_update
            existing_quake.magnitude = quake["magnitude"]
            existing_quake.tsunami = quake["tsunami"]
            existing_quake.longitude = quake["longitude"]
            existing_quake.latitude = quake["latitude"]
        else:
            new_quake = model.Quake(
                id = quake["id"],
                tsunami = quake["tsunami"],
                timestamp = quake["timestamp"],
                updated = quake_update,
                magnitude = quake["magnitude"],
                latitude = quake["latitude"],
                longitude = quake["longitude"]
            )
            model.session.add(new_quake)
    model.session.commit()

@app.route("/read_quakes_from_db")
def read_quakes_from_db():
    historical_quake_data = model.session.query(model.Quake).filter(model.Quake.magnitude >= 6).all()
    response_dict = {}
    
    for quake in historical_quake_data:
        quake_time = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=(quake.timestamp/1000)) # converted to sec
        quake_year = quake_time.strftime("%Y")

        # sort quakes by year for slider
        response_dict.setdefault(quake_year, []).append({
                "id": quake.id, "timestamp": quake.timestamp,
                "latitude": quake.latitude, "longitude": quake.longitude,
                "magnitude": quake.magnitude, "tsunami": quake.tsunami})
    return json.dumps(response_dict)
    
if __name__ == "__main__":
    socketio.run(app)