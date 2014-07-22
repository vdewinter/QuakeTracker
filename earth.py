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
last_update = "1406001828000" # need to reseed DB just before deploy? may not need to strip ms from below vars- 
# In gen, get last_update from db... when was last time run
recorded_min_magnitude = 6

@app.route("/reformat_new_quake_json")
def reformat_new_quake_json(update):
    update_release_time = str(update["metadata"]["generated"])
    update_release_time = int(update_release_time)
    global last_update
    print "first update %s" % last_update
    last_update = update_release_time 
    print "updated last_update %s" % last_update
    new_quake_dict = {}

    if update_release_time > last_update:
        for quake in update["features"]:
            props = quake["properties"]
            quake_updated = props["updated"]
            quake_magnitude = props["mag"]

            # are following conditions sufficient?
            if quake_updated > last_update and quake_magnitude >= recorded_min_magnitude:
                quake_id = quake["id"]
                quake_time = props["time"]
                quake_tsunami = props["tsunami"]
                quake_latitude = quake["geometry"]["coordinates"][1]
                quake_longitude = quake["geometry"]["coordinates"][0] 
        
                new_quake_dict[quake_id] = {"time":quake_time, "updated":quake_updated,
                    "magnitude":quake_magnitude, "tsunami":quake_tsunami, 
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

@app.route("/read_quakes_from_db")
def read_quakes_from_db():
    now = int(time.time())
    delta = 500 * 365.242 * 86400 # 500 years of seconds
    start_epoch = int(now - delta)

    historical_quake_data = model.session.query(model.Quake).filter(model.Quake.timestamp >= start_epoch).all()
    response_dict = {}

    for quake in historical_quake_data:
        shortened_quake_timestamp = int(str(quake.timestamp)[:-3]) # strip milliseconds
        converted_date = datetime.datetime.fromtimestamp(shortened_quake_timestamp)
        year = converted_date.strftime("%Y")
        month = converted_date.strftime("%m")
        day = converted_date.strftime("%d")

        response_dict.setdefault(year, []).append({
                "id": quake.id, "timestamp": quake.timestamp, 
                "month": month, "day": day, "year": year,
                "latitude": quake.latitude, "longitude": quake.longitude,
                "magnitude": quake.magnitude, "tsunami": quake.tsunami})

    return json.dumps(response_dict)
    
if __name__ == "__main__":
    socketio.run(app)