import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from models import DataPoint
import logging


def generate_sample_data(num_points, start_date, end_date, include_anomalies=True, anomaly_percentage=0.1, dataset_id=None):
    """
    Generate synthetic energy consumption data for testing.
    
    Args:
        num_points: Number of data points to generate
        start_date: Starting date for the data
        end_date: Ending date for the data
        include_anomalies: Whether to include anomalies in the data
        anomaly_percentage: Percentage of data points that should be anomalies (0.0-1.0)
        dataset_id: ID of the dataset these points belong to
        
    Returns:
        List of DataPoint objects
    """
    try:
        # Calculate date range and time intervals
        date_range = (end_date - start_date).days
        if date_range <= 0:
            raise ValueError("End date must be after start date")
        
        if num_points <= 0:
            raise ValueError("Number of points must be positive")
        
        # Interval between data points in hours
        interval_hours = max((date_range * 24) / num_points, 0.5)  # At least 30 minutes between points
        
        # Generate timestamps
        timestamps = []
        current_time = datetime.combine(start_date, datetime.min.time())
        
        for _ in range(num_points):
            timestamps.append(current_time)
            current_time += timedelta(hours=interval_hours)
            if current_time > datetime.combine(end_date, datetime.max.time()):
                break
        
        # Generate base energy consumption with daily and weekly patterns
        energy_data = []
        temperatures = []
        humidity_values = []
        occupancy_values = []
        
        for ts in timestamps:
            # Base consumption
            base = 10 + 2 * np.sin(ts.hour / 12 * np.pi)  # Daily cycle
            
            # Add weekly pattern (weekends have lower consumption)
            weekly_factor = 0.7 if ts.weekday() >= 5 else 1.0  # 5,6 = Sat,Sun
            
            # Add seasonality (if data spans multiple months)
            month_factor = 1.0 + 0.2 * np.sin((ts.month - 1) / 12 * 2 * np.pi)  # Annual cycle
            
            # Calculate consumption with patterns
            consumption = base * weekly_factor * month_factor
            
            # Add random noise
            noise = np.random.normal(0, 0.5)
            consumption += noise
            
            # Generate related features
            temperature = 20 + 10 * np.sin((ts.hour - 12) / 24 * 2 * np.pi) + np.random.normal(0, 2)  # Daily temperature cycle
            humidity = 50 + 10 * np.sin((ts.hour - 6) / 24 * 2 * np.pi) + np.random.normal(0, 5)  # Daily humidity cycle
            
            # Occupancy (business hours on weekdays)
            if 8 <= ts.hour <= 18 and ts.weekday() < 5:  # Weekday business hours
                occupancy = max(0, int(15 + np.random.normal(0, 5)))  # Random occupancy around 15
            else:
                occupancy = max(0, int(np.random.normal(0, 1)))  # Mostly 0 with occasional 1
            
            energy_data.append(consumption)
            temperatures.append(temperature)
            humidity_values.append(humidity)
            occupancy_values.append(occupancy)
        
        # Add anomalies if requested
        if include_anomalies and anomaly_percentage > 0:
            num_anomalies = int(num_points * anomaly_percentage)
            anomaly_indices = np.random.choice(range(num_points), size=num_anomalies, replace=False)
            
            for idx in anomaly_indices:
                # Create different types of anomalies
                anomaly_type = np.random.choice(['spike', 'drop', 'shift'])
                
                if anomaly_type == 'spike':
                    # Sudden spike in energy consumption (e.g., equipment malfunction)
                    energy_data[idx] *= (2 + np.random.random())
                
                elif anomaly_type == 'drop':
                    # Sudden drop in energy consumption (e.g., power outage, sensor error)
                    energy_data[idx] *= (0.1 + np.random.random() * 0.3)
                
                elif anomaly_type == 'shift':
                    # Sustained shift in consumption (e.g., new equipment, operational change)
                    shift_length = min(int(np.random.exponential(3)), num_points - idx)
                    shift_factor = 1.5 + np.random.random() * 0.5
                    
                    for i in range(idx, min(idx + shift_length, num_points)):
                        energy_data[i] *= shift_factor
        
        # Create DataPoint objects
        data_points = []
        for i in range(len(timestamps)):
            data_point = DataPoint(
                timestamp=timestamps[i],
                energy_consumption=max(0, energy_data[i]),  # Ensure non-negative
                temperature=temperatures[i],
                humidity=humidity_values[i],
                occupancy=occupancy_values[i],
                dataset_id=dataset_id
            )
            data_points.append(data_point)
        
        return data_points
    
    except Exception as e:
        logging.error(f"Error generating sample data: {str(e)}")
        raise
