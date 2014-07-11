from flask import Flask, render_template, redirect, request, flash
# from flask_sockets import Sockets
import model

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

@app.route('/read_db')
# gets every quake from DB - loop thru and format in dictionary- send as json to js
def read_db():
    historical_quake_data = model.session.query(model.Quake).all()
    response = {}
    for quake in historical_quake_data:
        response["id"] = quake.id
        respsonse["properties"]["latitude"] = quake.latitude
        respsonse["properties"]["longitude"] = quake.longitude

        magnitudes = [quake.magnitude_mw, quake.magnitude_ms, 
        quake.magnitude_mb, quake.magnitude_ml, quake.magnitude_mfa, 
        quake.magnitude_unk]
        avg_magnitude = sum(magnitudes)/len(magnitudes) if len(magnitudes) > 0 else float('nan')

        repsone["properties"]["magnitude"] = avg_magnitude 


if __name__ == "__main__":
    app.run(debug=True)
