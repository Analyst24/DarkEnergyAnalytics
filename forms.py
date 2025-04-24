from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FloatField, IntegerField, SelectField, FileField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please use a different one.')


class GenerateDataForm(FlaskForm):
    name = StringField('Dataset Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    num_data_points = IntegerField('Number of Data Points', validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()], format='%Y-%m-%d')
    end_date = DateField('End Date', validators=[DataRequired()], format='%Y-%m-%d')
    include_anomalies = SelectField('Include Anomalies', choices=[('yes', 'Yes'), ('no', 'No')], default='yes')
    anomaly_percentage = FloatField('Anomaly Percentage', validators=[Optional()])
    submit = SubmitField('Generate Data')


class UploadDataForm(FlaskForm):
    name = StringField('Dataset Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    data_file = FileField('Upload CSV File', validators=[Optional()])
    submit = SubmitField('Upload Data')


class ManualDataEntryForm(FlaskForm):
    timestamp = DateField('Date', validators=[DataRequired()], format='%Y-%m-%d')
    energy_consumption = FloatField('Energy Consumption (kWh)', validators=[DataRequired()])
    temperature = FloatField('Temperature (°C)', validators=[Optional()])
    humidity = FloatField('Humidity (%)', validators=[Optional()])
    occupancy = IntegerField('Occupancy', validators=[Optional()])
    submit = SubmitField('Add Data Point')


class AnomalyDetectionForm(FlaskForm):
    dataset = SelectField('Select Dataset', coerce=int, validators=[DataRequired()])
    algorithm = SelectField('Detection Algorithm', choices=[
        ('isolation_forest', 'Isolation Forest'),
        ('kmeans_clustering', 'K-means Clustering'),
        ('auto_encoder', 'Autoencoder (Deep Learning)'),
    ], default='isolation_forest')
    contamination = FloatField('Contamination Factor (0.01-0.5)', validators=[Optional()], default=0.1)
    submit = SubmitField('Detect Anomalies')
