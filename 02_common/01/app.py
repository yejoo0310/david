from flask import Flask, render_template

app = Flask(__name__)

@app.route("/test1")
def test1():
    return render_template('test1.html')


if __name__ == '__main__':
    app.run('0.0.0.0', 80)
