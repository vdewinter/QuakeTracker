from flask import Flask, render_template, redirect, request, flash, jsonify
from flask.ext.socketio import SocketIO, emit
import model, new_earthquakes
import json
from datetime import date
import time

app = Flask(__name__)
app.secret_key = 'secret_key' # change
socketio = SocketIO(app)
thread = None

# change this to broadcast only when new earthquakes published
# look at gevent
def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        time.sleep(10)
        count += 1
        socketio.emit('my response',
                      {'data': 'Server generated event', 'count': count}) # where does this emit code go


        # also put new events into DB
        # map session[socket]:last quake seen

@socketio.on("new earthquake")
def handle_custom_json(json):
    message = new_earthquakes.new_earthquake
    socketio.emit("new_earthquake", {"data": message}, json=True, broadcast=True)

@app.route('/')
def index():
    return render_template("index.html")

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
# add new data since last update to db
def write_new_quakes_to_db():
    pass

if __name__ == "__main__":
    socketio.run(app)