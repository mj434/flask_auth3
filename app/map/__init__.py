import csv
import json
import logging
import os

from flask import Blueprint, render_template, flash, abort, url_for, current_app, jsonify
from flask_login import current_user, login_required
from jinja2 import TemplateNotFound

from app.map.forms import location_edit_form, add_location_form

from app.db import db
from app.db.models import Location
from app.songs.forms import csv_upload
from werkzeug.utils import secure_filename, redirect
from flask import Response

map = Blueprint('map', __name__,
                        template_folder='templates')

@map.route('/locations', methods=['GET'], defaults={"page": 1})
@map.route('/locations/<int:page>', methods=['GET'])
def browse_locations(page):
    page = page
    per_page = 10
    pagination = Location.query.paginate(page, per_page, error_out=False)
    data = pagination.items
    edit_url = ('map.edit_location', [('location_id', ':id')])      #call funcn to save to db
    new_url = url_for('map.add_location')
    delete_url = ('map.delete_location', [('location_id', ':id')])
    try:
        return render_template('browse_locations.html',
                               data=data,
                               pagination=pagination,
                               Location=Location,
                               edit_url=edit_url,
                               new_url=new_url,
                               delete_url=delete_url)
    except TemplateNotFound:
        abort(404)

@map.route('/locations_datatables/', methods=['GET'])
def browse_locations_datatables():

    data = Location.query.all()

    try:
        return render_template('browse_locations_datatables.html',data=data)
    except TemplateNotFound:
        abort(404)

@map.route('/api/locations/', methods=['GET'])
def api_locations():
    data = Location.query.all()
    try:
        return jsonify(data=[location.serialize() for location in data])
    except TemplateNotFound:
        abort(404)


@map.route('/locations/map', methods=['GET'])
def map_locations():
    google_api_key = current_app.config.get('GOOGLE_API_KEY')
    try:
        return render_template('map_locations.html',google_api_key=google_api_key)
    except TemplateNotFound:
        abort(404)



@map.route('/locations/upload', methods=['POST', 'GET'])
@login_required
def location_upload():
    form = csv_upload()
    if form.validate_on_submit():
        filename = secure_filename(form.file.data.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        form.file.data.save(filepath)
        list_of_locations = []
        with open(filepath) as file:
            csv_file = csv.DictReader(file)
            list_of_locations = []
            for row in csv_file:
                location = Location.query.filter_by(title=row['location']).first()
                if location is None:
                    list_of_locations.append(Location(row['location'],row['longitude'],row['latitude'],row['population']))

        current_user.locations = list_of_locations
        db.session.commit()

        return redirect(url_for('map.browse_locations'))

    try:
        return render_template('upload_locations.html', form=form)
    except TemplateNotFound:
        abort(404)

@map.route('/locations/<int:location_id>/edit', methods=['POST', 'GET'])
@login_required
def edit_location(location_id):
    location = Location.query.get(location_id)
    form = location_edit_form(obj=location)
    if form.validate_on_submit():
        location.title = form.title.data
        location.latitude = form.latitude.data
        location.longitude = form.longitude.data
        location.population = form.population.data
        db.session.add(location)
        db.session.commit()
        flash('Location Edited Successfully', 'success')
        current_app.logger.info("edited a location")
        return redirect(url_for('map.browse_locations'))
    return render_template('location_edit.html', form=form)

@map.route('/locations/<int:location_id>/delete', methods=['POST'])
@login_required
def delete_location(location_id):
    location_id = Location.query.get(location_id)
    if location_id == 2:
        flash("id = 2 location deleted!")
    db.session.delete(location_id)
    db.session.commit()
    flash('Location was Deleted', 'success')
    return redirect(url_for('map.browse_locations'), 302)

#adding function add location now
@map.route('/locations/new', methods=['POST', 'GET'])
@login_required
def add_location():
    form = add_location_form()
    if form.validate_on_submit():
        title = Location.query.filter_by(title=form.title.data).first()
        if title is None:
            location = Location(title=form.title.data, longitude=form.longitude.data,
                                latitude=form.latitude.data, population=form.population.data)
            db.session.add(location)
            db.session.commit()
            flash('Location was created!', 'success')
            return redirect(url_for('map.browse_locations'))
        else:
            flash('A new city location was already created')
            return redirect(url_for('map.browse_locations'))
    return render_template('location_new.html', form=form)
