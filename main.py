import json
from datetime import datetime
from threading import Thread
from replit.database.database import ObservedList, ObservedDict
from flask import Flask, jsonify, render_template, request, url_for
from flask_cors import CORS
from replit import db
import pytz
# import ML

app = Flask(__name__)
CORS(app)

@app.route('/delete_sesa')
def delete():
  del db["sesa"]
  return "Deleted"

@app.route("/post_data_2", methods=["POST"])
def post_data_2():
    req_data = request.get_json()
    timestamp = datetime.now().astimezone(pytz.timezone('Asia/Jakarta')).isoformat()
    current = req_data.get("current")
    volt = req_data.get("voltage")

    if current is not None and volt is not None:
      if "sesa" not in db:
          db["sesa"] = []
          tmp = db["sesa"]
      else:
          tmp = db["sesa"]
      new_data = {"timestamp": timestamp, "current": current, "voltage": volt}
      tmp.append(new_data)
      db["sesa"] = tmp  # Set the updated value back
          
      return jsonify({"success": True, "message": "Data saved successfully"})
    else:
        return jsonify({"success": False, "message": "Invalid data format"})

@app.route("/get_db_data", methods=["GET"])
def get_db_data():
  data = []
  temp = {}
  for val in list(db["sesa"].value):
    if type(val) in [ObservedDict]:
      data.append(val.value)
      temp = {"data" : data}
      # Mengambil data terakhir dari data.json
      latest_data = temp["data"][-1] if temp["data"] else {}
  if latest_data:
    return jsonify(latest_data)
  else:
    return jsonify({"success": False, "message": "No data available"})

@app.route("/get_power", methods=["GET"])
def get_power():
  data = []
  temp = {}
  power = []
  for val in list(db["sesa"].value):
    if type(val) in [ObservedDict]:
      data.append(val.value)
      for i in range(len(data)):
        power.append({
            "timestamp": data[i]["timestamp"],
            "power": data[i]["current"] * data[i]["voltage"]
        })

      temp = {"data" : power}
      # Mengambil data terakhir dari data.json
      latest_data = temp["data"][-1] if temp["data"] else {}
  if latest_data:
    return jsonify(latest_data)
  else:
    return jsonify({"success": False, "message": "No data available"})


######################## ML DEPLOY ##########################
# predict = ML.data_frame(url_for("get_power"))
# predict_clean = ML.cleansing(predict)
# print(predict_clean)

######################## DATA HANDLING #########################
@app.route("/save_data", methods=["POST"])
def save_data():
    req_data = request.get_json()
    timestamp = req_data.get("timestamp")
    current = req_data.get("current")
    volt = req_data.get("volt")

    if timestamp and current and volt:
        db[timestamp] = {"current": current, "volt": volt}
        return jsonify({"success": True, "message": "Data saved successfully"})
    else:
        return jsonify({"success": False, "message": "Invalid data format"})


@app.route("/get_all_data", methods=["GET"])
def get_all_data():
    return jsonify(dict(db))

@app.route("/get_data_by_timestamp", methods=["GET"])
def get_data_by_timestamp():
    timestamp = request.args.get("timestamp")
    if not timestamp:
        return jsonify({"success": False, "message": "Timestamp parameter is missing"})

    data = db.get(timestamp)
    if data:
        return jsonify(data)
    else:
        return jsonify({"success": False, 
        "message": "Data not found for the provided timestamp"})

#################################################################
@app.route("/")
@app.route("/dashboard")
def dashboard():
  return render_template("dashboard.html")

@app.route("/dashboard_2")
def dashboard_2():
  return render_template("dashboard_2.html")

 

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=80)  # Bind to all interfaces