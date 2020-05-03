from flask import Flask
from flask import render_template

from radiation_model.radiation_calculator import wall_radiation
app = Flask(__name__)


@app.route('/')
def main_app():
    rad_list = wall_radiation(28, 20, 13, 1, 5, 6, 1, 1)
    print(rad_list)
    output_list = []
    [output_list.append(f'x: {item.x} z: {item.z} N: {item.rad}') for item in rad_list]
    return render_template('main.html', list=output_list)


if __name__ == '__main__':
    app.run(debug=True)