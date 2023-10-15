from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room, send

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"
socketio = SocketIO(app)

rooms = {}

@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        name = request.form.get("name")
        room = request.form.get("room")

        if not name or not room:
            return render_template("home.html", error="Please enter a name and room.")

        session["name"] = name
        session["room"] = room
        return redirect(url_for("room"))

    return render_template("home.html")

@app.route("/room")
def room():
    name = session.get("name")
    room = session.get("room")

    if not name or not room:
        return redirect(url_for("home"))

    return render_template("room.html", name=name, room=room)

@socketio.on("message")
def message(data):
    room = session.get("room")
    name = session.get("name")

    content = {
        "name": name,
        "message": data["data"],
    }
    
    send(content, room=room)

@socketio.on("connect")
def connect():
    name = session.get("name")
    room = session.get("room")

    join_room(room)
    send({"name": name, "message": "has entered the room."}, room=room)

@socketio.on("disconnect")
def disconnect():
    name = session.get("name")
    room = session.get("room")

    leave_room(room)
    send({"name": name, "message": "has left the room."}, room=room)

if __name__ == "__main__":
    socketio.run(app, debug=True)
