from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField
from wtforms import SubmitField
from wtforms.validators import DataRequired


class GameForm(FlaskForm):
    icon = FileField('Icon of game', validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField("Description")
    submit = SubmitField('Submit')
