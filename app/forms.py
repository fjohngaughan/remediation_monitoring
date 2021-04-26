from flask_sqlalchemy.model import camel_to_snake_case
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, widgets
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from wtforms.validators import DataRequired, EqualTo, Email
from app.models import User, Site 

class MultiCheckboxField(QuerySelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class UserInfoForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField()

class UpdateUserInfoForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField()

class UpdatePasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField()

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField("Login")

class AddSiteForm(FlaskForm):
    site_name = StringField('Site Name', validators=[DataRequired()])
    gt_global_id = StringField('GeoTracker Global ID', validators=[DataRequired()])
    submit = SubmitField("Add Site")

class EditSiteForm(FlaskForm):
    site_name = StringField('Site Name', validators=[DataRequired()])
    submit = SubmitField('Save')

class AddReportForm(FlaskForm):
    report_name = StringField('Report Name', validators=[DataRequired()])
    current_user_sites = MultiCheckboxField("Select Sites", query_factory=lambda: Site.query.filter_by(user_id=current_user.id).all())
    description = TextAreaField('Description')
    submit = SubmitField('Create Report')