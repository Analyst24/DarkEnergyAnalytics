from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from app import app, db
from models import User, Dataset, DataPoint, Anomaly, ModelEvaluation, Recommendation
from forms import LoginForm, SignupForm, GenerateDataForm, UploadDataForm, ManualDataEntryForm, AnomalyDetectionForm
from data_generator import generate_sample_data
from anomaly_detection import detect_anomalies, evaluate_model, generate_recommendations
import pandas as pd
import io
from datetime import datetime
import logging


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check username and password.', 'danger')
    
    return render_template('login.html', title='Login', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = SignupForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html', title='Sign Up', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    # Get user statistics for dashboard
    datasets_count = Dataset.query.filter_by(user_id=current_user.id).count()
    anomalies_count = Anomaly.query.join(Dataset).filter(Dataset.user_id == current_user.id).count()
    recommendations_count = Recommendation.query.join(Dataset).filter(Dataset.user_id == current_user.id).count()
    
    # Get recent datasets
    recent_datasets = Dataset.query.filter_by(user_id=current_user.id).order_by(Dataset.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                          title='Dashboard',
                          datasets_count=datasets_count,
                          anomalies_count=anomalies_count,
                          recommendations_count=recommendations_count,
                          recent_datasets=recent_datasets)


@app.route('/generate-data', methods=['GET', 'POST'])
@login_required
def generate_data():
    form = GenerateDataForm()
    
    if form.validate_on_submit():
        try:
            # Create a new dataset
            dataset = Dataset(
                name=form.name.data,
                description=form.description.data,
                user_id=current_user.id,
                is_sample=True
            )
            db.session.add(dataset)
            db.session.flush()  # Get the dataset ID without committing
            
            # Generate sample data
            include_anomalies = form.include_anomalies.data == 'yes'
            anomaly_percentage = form.anomaly_percentage.data if include_anomalies else 0
            
            data_points = generate_sample_data(
                num_points=form.num_data_points.data,
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                include_anomalies=include_anomalies,
                anomaly_percentage=anomaly_percentage,
                dataset_id=dataset.id
            )
            
            # Add data points to the database
            db.session.add_all(data_points)
            db.session.commit()
            
            flash(f'Successfully generated {len(data_points)} data points!', 'success')
            return redirect(url_for('view_anomalies'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error generating data: {str(e)}', 'danger')
            logging.error(f"Data generation error: {str(e)}")
    
    return render_template('generate_data.html', title='Generate Sample Data', form=form)


@app.route('/custom-data', methods=['GET', 'POST'])
@login_required
def custom_data():
    upload_form = UploadDataForm()
    manual_form = ManualDataEntryForm()
    
    # Get user datasets for display
    datasets = Dataset.query.filter_by(user_id=current_user.id).order_by(Dataset.created_at.desc()).all()
    
    # Process file upload
    if upload_form.validate_on_submit() and 'data_file' in request.files:
        try:
            file = request.files['upload_form-data_file']
            if file.filename:
                # Create new dataset
                dataset = Dataset(
                    name=upload_form.name.data,
                    description=upload_form.description.data,
                    user_id=current_user.id,
                    is_sample=False
                )
                db.session.add(dataset)
                db.session.flush()
                
                # Read and process the CSV file
                stream = io.StringIO(file.stream.read().decode('utf-8'))
                df = pd.read_csv(stream)
                
                # Process each row and add to database
                data_points = []
                for _, row in df.iterrows():
                    # Assuming CSV has required columns
                    data_point = DataPoint(
                        timestamp=datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S'),
                        energy_consumption=float(row['energy_consumption']),
                        temperature=float(row.get('temperature', 0)) if 'temperature' in row else None,
                        humidity=float(row.get('humidity', 0)) if 'humidity' in row else None,
                        occupancy=int(row.get('occupancy', 0)) if 'occupancy' in row else None,
                        dataset_id=dataset.id
                    )
                    data_points.append(data_point)
                
                db.session.add_all(data_points)
                db.session.commit()
                
                flash(f'Successfully uploaded {len(data_points)} data points!', 'success')
                return redirect(url_for('custom_data'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error processing uploaded file: {str(e)}', 'danger')
            logging.error(f"Upload error: {str(e)}")
    
    # Process manual data entry
    elif manual_form.validate_on_submit():
        try:
            # Check if we need to create a new dataset or use an existing one
            dataset_id = request.form.get('dataset_id')
            
            if not dataset_id or dataset_id == 'new':
                # Create a new dataset for manual entry
                dataset = Dataset(
                    name=f"Manual Data - {datetime.now().strftime('%Y-%m-%d')}",
                    description="Manually entered data points",
                    user_id=current_user.id,
                    is_sample=False
                )
                db.session.add(dataset)
                db.session.flush()
                dataset_id = dataset.id
            
            # Create new data point
            data_point = DataPoint(
                timestamp=manual_form.timestamp.data,
                energy_consumption=manual_form.energy_consumption.data,
                temperature=manual_form.temperature.data,
                humidity=manual_form.humidity.data,
                occupancy=manual_form.occupancy.data,
                dataset_id=dataset_id
            )
            
            db.session.add(data_point)
            db.session.commit()
            
            flash('Data point added successfully!', 'success')
            return redirect(url_for('custom_data'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding data point: {str(e)}', 'danger')
            logging.error(f"Manual data entry error: {str(e)}")
    
    return render_template('custom_data.html', 
                          title='Custom Data',
                          upload_form=upload_form,
                          manual_form=manual_form,
                          datasets=datasets)


@app.route('/view-anomalies', methods=['GET', 'POST'])
@login_required
def view_anomalies():
    form = AnomalyDetectionForm()
    
    # Populate the dataset choices
    datasets = Dataset.query.filter_by(user_id=current_user.id).all()
    form.dataset.choices = [(d.id, d.name) for d in datasets]
    
    # Process anomaly detection form
    if form.validate_on_submit():
        try:
            dataset_id = form.dataset.data
            algorithm = form.algorithm.data
            contamination = form.contamination.data or 0.1
            
            # Run anomaly detection
            dataset = Dataset.query.get_or_404(dataset_id)
            anomalies = detect_anomalies(dataset, algorithm, contamination)
            
            # Store anomalies in the database
            db.session.add_all(anomalies)
            
            # Run model evaluation
            evaluation = evaluate_model(dataset, algorithm, anomalies)
            db.session.add(evaluation)
            
            # Generate recommendations based on anomalies
            recommendations = generate_recommendations(dataset, anomalies)
            db.session.add_all(recommendations)
            
            db.session.commit()
            
            flash(f'Successfully detected {len(anomalies)} anomalies!', 'success')
            return redirect(url_for('view_anomalies'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error detecting anomalies: {str(e)}', 'danger')
            logging.error(f"Anomaly detection error: {str(e)}")
    
    # Get datasets and their anomalies for display
    datasets_with_anomalies = []
    for dataset in datasets:
        anomalies = Anomaly.query.filter_by(dataset_id=dataset.id).all()
        if anomalies:
            datasets_with_anomalies.append({
                'dataset': dataset,
                'anomalies': anomalies,
                'count': len(anomalies)
            })
    
    return render_template('view_anomalies.html', 
                          title='View Anomalies',
                          form=form,
                          datasets_with_anomalies=datasets_with_anomalies)


@app.route('/model-evaluation')
@login_required
def model_evaluation():
    # Get all model evaluations for the current user
    evaluations = (ModelEvaluation.query
                  .join(Dataset)
                  .filter(Dataset.user_id == current_user.id)
                  .order_by(ModelEvaluation.created_at.desc())
                  .all())
    
    # Group evaluations by dataset for easier display
    evaluations_by_dataset = {}
    for eval in evaluations:
        if eval.dataset_id not in evaluations_by_dataset:
            evaluations_by_dataset[eval.dataset_id] = {
                'dataset': eval.dataset,
                'evaluations': []
            }
        evaluations_by_dataset[eval.dataset_id]['evaluations'].append(eval)
    
    return render_template('model_evaluation.html',
                          title='Model Evaluation',
                          evaluations_by_dataset=evaluations_by_dataset)


@app.route('/recommendations')
@login_required
def recommendations():
    # Get all recommendations for the current user
    recommendations = (Recommendation.query
                      .join(Dataset)
                      .filter(Dataset.user_id == current_user.id)
                      .order_by(Recommendation.created_at.desc())
                      .all())
    
    return render_template('recommendations.html',
                          title='Recommendations',
                          recommendations=recommendations)


@app.route('/api/dataset/<int:dataset_id>/data')
@login_required
def get_dataset_data(dataset_id):
    # Verify the dataset belongs to the current user
    dataset = Dataset.query.filter_by(id=dataset_id, user_id=current_user.id).first_or_404()
    
    # Get data points for the dataset
    data_points = DataPoint.query.filter_by(dataset_id=dataset_id).order_by(DataPoint.timestamp).all()
    
    # Get anomalies
    anomalies = Anomaly.query.filter_by(dataset_id=dataset_id).all()
    anomaly_data_point_ids = [a.data_point_id for a in anomalies]
    
    # Format data for chart.js
    data = {
        'timestamps': [dp.timestamp.strftime('%Y-%m-%d %H:%M:%S') for dp in data_points],
        'energy_consumption': [dp.energy_consumption for dp in data_points],
        'temperature': [dp.temperature for dp in data_points if dp.temperature is not None],
        'humidity': [dp.humidity for dp in data_points if dp.humidity is not None],
        'is_anomaly': [1 if dp.id in anomaly_data_point_ids else 0 for dp in data_points]
    }
    
    return jsonify(data)


@app.route('/api/dataset/<int:dataset_id>/anomalies')
@login_required
def get_dataset_anomalies(dataset_id):
    # Verify the dataset belongs to the current user
    dataset = Dataset.query.filter_by(id=dataset_id, user_id=current_user.id).first_or_404()
    
    # Get anomalies and join with data points to get timestamps
    anomalies = (Anomaly.query
                .join(DataPoint, Anomaly.data_point_id == DataPoint.id)
                .filter(Anomaly.dataset_id == dataset_id)
                .with_entities(
                    Anomaly.id,
                    Anomaly.anomaly_score,
                    Anomaly.algorithm,
                    DataPoint.timestamp,
                    DataPoint.energy_consumption,
                    DataPoint.temperature,
                    DataPoint.humidity,
                    DataPoint.occupancy
                )
                .all())
    
    # Format data
    result = [{
        'id': a.id,
        'timestamp': a.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'score': a.anomaly_score,
        'algorithm': a.algorithm,
        'energy_consumption': a.energy_consumption,
        'temperature': a.temperature,
        'humidity': a.humidity,
        'occupancy': a.occupancy
    } for a in anomalies]
    
    return jsonify(result)
