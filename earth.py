from flask import Flask, render_template, redirect, request, flash
# from flask_sockets import Sockets
import model
import json

app = Flask(__name__)
app.secret_key = 'secret_key' # change
# sockets = Sockets(app)

# @sockets.route('/echo')
# def echo_socket(ws):
#     while True:
#         message = ws.receieve()
#         ws.send(message)

@app.route('/')
def index():
    return render_template("index.html")
# I want to make this all one page- how should I organize requests here

@app.route("/read_quakes_from_db")
# gets every quake from DB - loop thru and format in dictionary- send as json to js
def read_quakes_from_db():
    historical_quake_data = model.session.query(model.Quake).all()
    response_list = []

    for quake in historical_quake_data:
        response = {}
        
        response["id"] = quake.id
        response["latitude"] = quake.latitude
        response["longitude"] = quake.longitude

        response["year"] = quake.year
        response["month"] = quake.month
        response["day"] = quake.day
        response["hour"] = quake.hour

        magnitudes = [quake.magnitude_mw, quake.magnitude_ms, 
        quake.magnitude_mb, quake.magnitude_ml, quake.magnitude_mfa, 
        quake.magnitude_unk]
        magnitudes_to_average = []
        for i in magnitudes:
            if i:
                magnitudes_to_average.append(float(i))
        if len(magnitudes_to_average) > 0:
            avg_magnitude = sum(magnitudes_to_average)/float(len(magnitudes_to_average)) 
        else:
            avg_magnitude = None
        response["magnitude"] = avg_magnitude 

        response_list.append(response)

    return json.dumps(response_list)

@app.route("/write_new_quakes_to_db")
# add new data since last update to db
def write_new_quakes_to_db():
    pass

if __name__ == "__main__":
    app.run(debug=True)
