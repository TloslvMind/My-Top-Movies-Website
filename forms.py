from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm

class EditForm(FlaskForm):
    new_rating = StringField('new_rating', validators=[DataRequired()])
    new_review = StringField('new_review', validators=[DataRequired()])
    submit = SubmitField('Submit')


class AddMovie(FlaskForm):
    title = StringField('Movie Title', validators=[DataRequired()])
    submit = SubmitField('Add Movie')