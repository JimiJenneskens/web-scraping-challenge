from flask import Flask, render_template, request, redirect
from flask_pymongo import PyMongo
import pandas as pd 
import scrape_mars

# create flask
app = Flask(__name__)

# set up mongo connection
mongo = PyMongo(app, uri="mongodb://localhost:27017/app.py")


# create routes
@app.route("/")
def echo():
    m_facts = mongo.db.collection.find_one()
    return render_template("index.html", mars=m_facts)

@app.route("/scrape")
def scrape():
    # put scrape function in variable
    mars_data = scrape_mars.scrape_all()

    # update mongo database with data
    mongo.db.collection.update({}, mars_data, upsert=True)

    return redirect("/", code=302)



if __name__ == "__main__":
    app.run(debug=True)
