# TODO: make sure new quakes are writing to db when new report comes in (this means dynamic updating of hist points is broken)
# make  big circles look more clickable by changing mouse pointer
import model
import datetime
from flask import Flask, render_template
from flask.ext.socketio import SocketIO
import json
import os
import requests
from threading import Thread
import time

app = Flask(__name__)
app.debug = True
socketio = SocketIO(app)
thread = None

last_update = 0
USGS_URL = "http://earthquake.usgs.gov/earthquakes/feed/geojson/2.5/week"

# grab the last report update time from the database
# set up loop to request new report from USGS every minute
# reformat the data, send it to the client, and save it in the database
def background_thread():
    count = 0
    while True:
        time.sleep(60)
        count += 1
        reformatted_data = handle_new_quake_json()
        # emit new quakes in json format to client
        new_earthquakes_json = reformatted_data[0]
        socketio.emit('new_earthquake', new_earthquakes_json)
        # write new quakes in model object format to database if USGS not down
        new_earthquakes_models = reformatted_data[1]
        if new_earthquakes_models:
            write_new_quakes_to_db(new_earthquakes_models)

# set up background thread, render html
@app.route('/')
def index():
    return render_template("index.html")

def model_to_dict(model_list):
    pass
def json_to_model(json_string):
    pass

# function for reformatting new earthquake data
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

# make request to USGS server, handle status codes != 200
# update latest report timestamp in database, return reformatted report data to client as json,
# return report data as model objects to db
@socketio.on("new_earthquake")
@app.route("/new_earthquake")
def handle_new_quake_json():
    r = requests.get(USGS_URL)
    new_quakes_json = r.json()
    new_quake_list = []
    quake_models = []

    # read database and send to client all quakes from the last week
    #if r.status_code != 200:
    if True:
        print "USGS server down"

        # get epoch timestamp of one week ago
        ms_per_week = 604800000
        one_week_ago = (int(time.time()) * 1000) - ms_per_week
        new_quakes = model.session.query(model.Quake).filter(model.Quake.timestamp >= one_week_ago).all()
        print "model objects %s" % new_quakes
        new_quakes = model_to_dict(new_quakes)
    #  ^ this needs to be in a sequence

        for quake in new_quakes:
            new_quake_list.append(quake)
    else:
        # get latest report timestamp
        last_update = int(new_quakes_json["metadata"]["generated"])
        
        # update database with the latest report timestamp
        db_last_update = model.session.query(model.QuakeUpdate).one()
        db_last_update.update_time = last_update
        model.session.commit()

        new_data = new_quakes_json["features"]
        for quake in new_data:
            # create quake dict to send to client
            response = create_quake_dict(quake)
            new_quake_list.append(response)
            
        # create model objects to pass to write_to_db
        stringified_report = json.loads(new_data, "latin-1")
        for i in stringified_report:
            quake_models.append(i)

    # return new report data to send client as a json-encoded list of dictionaries/objects
    # return new report data in model object form for writing to db
    return (json.dumps(new_quake_list), quake_models) 

# update earthquakes from past week that are already in the database, otherwise add new earthquakes to database
def write_new_quakes_to_db(new_quake_dict):
    print "writing to db"
    db = model.session.query(model.Quake).all()

    # put database objects into dictionary for fast lookup
    db_objects = {}
    for obj in db:
        db_objects[obj.id] = obj

    for quake in new_quake_dict:
        # update earthquakes that are already in database if they were updated (re-estimated magnitude, etc.) after the quake occurred
        quake_update = int(quake["updated"])
        if quake["id"] in db_objects.keys() and (quake_update > int(quake["timestamp"])):
            print "updating quake %s" % quake["id"]
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

# read all magnitude 6 or greater earthquakes from the database
@app.route("/read_quakes_from_db")
def read_quakes_from_db():
    historical_quake_data = model.session.query(model.Quake).filter(model.Quake.magnitude >= 6).all()
    response_dict = {}
    
    # get year of each earthquake
    for quake in historical_quake_data:
        quake_time = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=(quake.timestamp/1000)) # converted to seconds
        quake_year = quake_time.strftime("%Y")

        # sort earthquakes by year for slider
        response_dict.setdefault(quake_year, []).append({
                "id": quake.id, "timestamp": quake.timestamp,
                "latitude": quake.latitude, "longitude": quake.longitude,
                "magnitude": quake.magnitude, "tsunami": quake.tsunami})

    # send json to client
    return json.dumps(response_dict)
    
thread = Thread(target=background_thread)
thread.start()

if __name__ == "__main__":
    port = os.environ.get('PORT', 5000)
    socketio.run(app, port=int(port))