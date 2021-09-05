from flask import Flask, request, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy

DBNAME = "population.sqlite3"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + DBNAME
app.config["SECRET_KEY"] = "wkjeqsdejnsxrgewkhvgfslsqf"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Region(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

    def __str__(self):
        return self.name


class Country(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    region_id = db.Column(db.Integer, db.ForeignKey("region.id"), nullable=False)
    population = db.Column(db.Integer, nullable=True)

    region = db.relationship(Region, backref=db.backref("population"))

    def __str__(self):
        return f"{self.name} ---> population: {self.population:,.0f}"

    def __lt__(self, other):
        return self.population > other.population


@app.route("/")
def start():
    return redirect(url_for("index"))


@app.route("/index")
def index():
    region_list = []
    regions = Region.query.order_by(Region.name)
    for region in regions:

        max_pop_in_region = max(Country.query.filter(Country.region == region).order_by(Country.population))
        min_pop_in_region = min(Country.query.filter(Country.region == region).order_by(Country.population))
        region_list.append([region, max_pop_in_region, min_pop_in_region])
    return render_template("index.html", region_list=region_list)


@app.template_filter()
def numberFormat(value):
    return format(int(value), ',d')


if __name__ == '__main__':
    app.run(debug=True, port=5001)
