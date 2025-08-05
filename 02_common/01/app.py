from flask import Flask, render_template

app = Flask(__name__)


@app.route("/menu")
def menu():
    return render_template("menu.html")

@app.route("/test4")
def test4():
    return render_template('test4.html')


if __name__ == '__main__':
    app.run('0.0.0.0', 80)
