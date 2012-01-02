#!/usr/bin/python
from flask import Flask, render_template, request, redirect, url_for

skyblock = Flask(__name__)
checked_boxes = []

@skyblock.route("/favicon.ico")
def favicon():
    return redirect(url_for('static', filename='favicon.ico'))

@skyblock.route("/")
def index():
    return render_template('index.html', checked=checked_boxes)

@skyblock.route("/store", methods=['POST'])
def store():
    if request.method == "POST":
        checked_boxes = request.data.split(',')[:-1]
        return "Saving succeeded"
    else:
        return "Only accepts POST"

if __name__ == "__main__":
    skyblock.run(debug=True)
