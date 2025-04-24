from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    datasets = db.relationship('Dataset', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Dataset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_sample = db.Column(db.Boolean, default=False)
    
    # Relationships
    data_points = db.relationship('DataPoint', backref='dataset', lazy=True, cascade="all, delete-orphan")
    anomalies = db.relationship('Anomaly', backref='dataset', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Dataset {self.name}>'


class DataPoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    energy_consumption = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=True)
    humidity = db.Column(db.Float, nullable=True)
    occupancy = db.Column(db.Integer, nullable=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.id'), nullable=False)
    
    def __repr__(self):
        return f'<DataPoint {self.timestamp}>'


class Anomaly(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_point_id = db.Column(db.Integer, db.ForeignKey('data_point.id'), nullable=False)
    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.id'), nullable=False)
    anomaly_score = db.Column(db.Float, nullable=False)
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    algorithm = db.Column(db.String(50), nullable=False)
    
    # Relationship
    data_point = db.relationship('DataPoint', backref='anomalies')
    
    def __repr__(self):
        return f'<Anomaly {self.id}>'


class ModelEvaluation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.id'), nullable=False)
    algorithm = db.Column(db.String(50), nullable=False)
    accuracy = db.Column(db.Float, nullable=True)
    precision = db.Column(db.Float, nullable=True)
    recall = db.Column(db.Float, nullable=True)
    f1_score = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    dataset = db.relationship('Dataset', backref='model_evaluations')
    
    def __repr__(self):
        return f'<ModelEvaluation {self.algorithm}>'


class Recommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.id'), nullable=False)
    anomaly_id = db.Column(db.Integer, db.ForeignKey('anomaly.id'), nullable=True)
    recommendation_text = db.Column(db.Text, nullable=False)
    potential_savings = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    dataset = db.relationship('Dataset', backref='recommendations')
    anomaly = db.relationship('Anomaly', backref='recommendations')
    
    def __repr__(self):
        return f'<Recommendation {self.id}>'
