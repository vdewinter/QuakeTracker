from flask import Flask, render_template, redirect, request, flash, jsonify
# from flask.ext.socketio import SocketIO, emit
import model
import json
from datetime import date

app = Flask(__name__)
app.secret_key = 'secret_key' # change
# socketio = SocketIO(app)

# message delivers a string payload, json and custome events deliver JSON in form of python dict
# events can be defined inside a namespace arg (optoinal) that allow a client to open mult connections 
# to the server that are multiplexed in a single socket. default is global namespace

# send sends string or JSON to client
# emit sends message under custom event name

# messages are sent to teh connected client by default but broadcast=True allows all clients connected
 # to the namespace to recieve the message
# @socketio.on('my event', namespace="/test")
# def test_message(message): 
#     emit("my response", {"data": message["data"]})

# @socketio.on("my broadcast event", namespace="/test")
# def test_message(message):
#     emit("my response", {"data": message["data"]}, broadcast = True)

# @socketio.on("connect", namespace="/test")
# def test_connect():
#     emit("my repsonse", {"data": "Connected"})

# @socketio.on("disconnect", namespace="/test")
# def test_disconenct():
#     print("client disconnected")

@app.route('/')
def index():
    return render_template("index.html")

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
    # socketio.run(app, debug=True)
    app.run(debug = True)
