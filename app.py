import flask, csv, sys, os, redis
from datetime import datetime
from os.path import join, dirname, realpath
from flask import Flask, send_file, after_this_request
from flask import render_template
from flask_session import Session

from radiation_model import radiation_calculator

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url('redis://127.0.0.1:6379')

sess = Session()
sess.init_app(app)

@app.route('/', methods=["GET"])
def main_app():
    return render_template("main.html", error_message=flask.request.args.get("error_message"))


@app.route('/list', methods=["POST"])
def calculate_result():
    try:
        if flask.request.form["type"] == "wall":
            func = radiation_calculator.wall_radiation
            header = "Расчет радиационного фона от стены"
        else:
            func = radiation_calculator.room_radiation
            header = "Расчет радиационного фона в комнате"
        rad_list = func(k=int(flask.request.form["k"]),
                        l=int(flask.request.form["l"]),
                        m=int(flask.request.form["m"]),
                        n=int(flask.request.form["n"]),
                        y0=int(flask.request.form["y0"]),
                        d=int(flask.request.form["d"]),
                        p=int(flask.request.form["p"]),
                        r=int(flask.request.form["r"]))
        insert_data_in_session(rad_list)
        output_list = []
        [output_list.append(f'x: {item.x} z: {item.z} N: {item.rad}') for item in rad_list]
        return render_template('list_result.html', list=output_list, header=header)
    except Exception:
        return flask.redirect(flask.url_for('main_app', error_message="Неверный формат вводимых данных"))


@app.route('/image', methods=["POST"])
def get_image():
    if flask.request.form["type"] == "wall":
        func = radiation_calculator.wall_radiation
        header = "Расчет радиационного фона от стены"
    else:
        func = radiation_calculator.room_radiation
        header = "Расчет радиационного фона в комнате"
    rad_list = func(k=int(flask.request.form["k"]),
                    l=int(flask.request.form["l"]),
                    m=int(flask.request.form["m"]),
                    n=int(flask.request.form["n"]),
                    y0=int(flask.request.form["y0"]),
                    d=int(flask.request.form["d"]),
                    p=int(flask.request.form["p"]),
                    r=int(flask.request.form["r"]))
    z, radiation = [], []
    for rad in rad_list:
        z.append(rad.z)
        radiation.append(rad.rad)
    z = z[-1]
    rad_array = []
    for i in range(0, len(radiation), z):
        rad_array.append(radiation[i:i+z])
    return render_template('image.html', rad=rad_array, header=header)


def insert_data_in_session(data):
    x, z, r = [], [], []
    for item in data:
        x.append(item.x)
        z.append(item.z)
        r.append(item.rad)
    flask.session["x"] = x
    flask.session["z"] = z
    flask.session["r"] = r


@app.route("/list/download", methods=["GET"])
def download_data():
    file_name = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    absolute_file_name = join(dirname(realpath(__file__)), f"tmp\\{file_name}")
    with open(absolute_file_name, "w+", newline='') as file:
        csv_writer = csv.writer(file, delimiter=',',)
        csv_writer.writerow(["x", "z", "N"])
        for x, z, rad in zip(flask.session["x"], flask.session["z"], flask.session["r"]):
            csv_writer.writerow([x, z, rad])

    return send_file(absolute_file_name, mimetype='text/csv',
                     attachment_filename=file_name,
                     as_attachment=True)


if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run(debug=True)
