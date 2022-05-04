from flask_wtf import FlaskForm
from wtforms import validators
from wtforms.fields import *

class location_edit_form(FlaskForm):
    title = StringField('Location', [validators.DataRequired(), ],
                        description="Location")
    longitude = StringField('Longitude', [validators.DataRequired(), ],
                            description="Longitude")
    latitude = StringField('Latitude', [validators.DataRequired(), ],
                           description="Latitude")
    population = IntegerField('Population', description="Please update the population")

    submit = SubmitField()

class csv_upload(FlaskForm):
    file = FileField()
    submit = SubmitField()

class add_location_form(FlaskForm):
    title = StringField('Location', [validators.DataRequired(), ],
                          description="Location")
    longitude = StringField('Longitude', [validators.DataRequired(), ],
                          description="Longitude")
    latitude = StringField('Latitude', [validators.DataRequired(), ],
                          description="Latitude")
    population = IntegerField('Population', [validators.DataRequired(), ],
                          description="Population")
    submit = SubmitField()
