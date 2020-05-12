import flask
from flask import Flask
from flask import render_template

from radiation_model import radiation_calculator

app = Flask(__name__)


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
        print("heh!")
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
    x, z, radiation = [], [], []
    for rad in rad_list:
        print(1)
        x.append(rad.x)
        z.append(rad.z)
        radiation.append(rad.rad)
    return render_template('image.html', x=x, z=z, rad=radiation, header=header)


if __name__ == '__main__':
    app.run(debug=True)
