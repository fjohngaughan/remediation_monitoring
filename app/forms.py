from flask_sqlalchemy.model import camel_to_snake_case
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from wtforms.validators import DataRequired, EqualTo, Email
from app.models import User, Site 

class UserInfoForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField()

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField()

class AddSiteForm(FlaskForm):
    site_name = StringField('Site Name', validators=[DataRequired()])
    gt_global_id = StringField('GeoTracker Global ID', validators=[DataRequired()])
    submit = SubmitField()

class AddReportForm(FlaskForm):
    report_name = StringField('Report Name', validators=[DataRequired()])
    # Think about changing this to checkboxes
    current_user_sites = QuerySelectMultipleField(query_factory=lambda: Site.query.filter_by(user_id=current_user.id).all())
    submit = SubmitField()