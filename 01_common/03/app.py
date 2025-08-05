import socket
from flask import Flask, render_template

app = Flask(__name__)


@app.route("/menu")
def menu():
    return render_template("menu.html")


@app.route("/")
def home():
    if app.debug:
        hostname = '컴퓨터(인스턴스) : ' + socket.gethostname()
    else:
        hostname = ' '
    return render_template("index.html", computername=hostname)


if __name__ == '__main__':
    # app.run('0.0.0.0', 80, debug=True)
    app.run('0.0.0.0', 80)
