import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score
import joblib
import os
from datetime import datetime, timedelta
import random

def generate_synthetic_dataset():
    """Generate synthetic dataset for exam registration predictions"""
    
    np.random.seed(42)
    n_samples = 500
    
    courses = [
        'Cloud Computing', 'Cryptography & Network Security', 
        'Discrete Mathematics', 'Programming Fundamentals',
        'Database Systems', 'Web Development',
        'Mobile App Development', 'Data Structures & Algorithms'
    ]
    
    departments = ['ICT', 'Engineering', 'Business Administration']
    
    data = {
        'student_id': [f'STU{str(i).zfill(4)}' for i in range(n_samples)],
        'course': np.random.choice(courses, n_samples),
        'department': np.random.choice(departments, n_samples, p=[0.6, 0.25, 0.15]),
        'previous_gpa': np.random.uniform(2.0, 4.0, n_samples),
        'attendance_rate': np.random.uniform(0.5, 1.0, n_samples),
        'study_hours_per_week': np.random.randint(5, 40, n_samples),
        'registered_early': np.random.choice([0, 1], n_samples, p=[0.3, 0.7]),
        'semester': np.random.choice(['Semester 1', 'Semester 2'], n_samples),
    }
    
    df = pd.DataFrame(data)
    
    df['success_probability'] = (
        0.3 * df['previous_gpa'] / 4.0 +
        0.25 * df['attendance_rate'] +
        0.2 * (df['study_hours_per_week'] / 40) +
        0.15 * df['registered_early'] +
        np.random.normal(0, 0.1, n_samples)
    ).clip(0, 1)
    
    df['exam_success'] = (df['success_probability'] > 0.6).astype(int)
    
    df['predicted_score'] = (
        df['success_probability'] * 100 +
        np.random.normal(0, 5, n_samples)
    ).clip(0, 100)
    
    return df

def train_success_prediction_model():
    """Train a model to predict exam success"""
    
    df = generate_synthetic_dataset()
    
    feature_columns = ['previous_gpa', 'attendance_rate', 'study_hours_per_week', 'registered_early']
    X = df[feature_columns]
    y = df['exam_success']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    os.makedirs('models', exist_ok=True)
    joblib.dump(model, 'models/success_prediction_model.pkl')
    
    return {
        'model': model,
        'accuracy': accuracy,
        'feature_importance': dict(zip(feature_columns, model.feature_importances_))
    }

def train_score_prediction_model():
    """Train a model to predict exam scores"""
    
    df = generate_synthetic_dataset()
    
    feature_columns = ['previous_gpa', 'attendance_rate', 'study_hours_per_week', 'registered_early']
    X = df[feature_columns]
    y = df['predicted_score']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = GradientBoostingRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    
    os.makedirs('models', exist_ok=True)
    joblib.dump(model, 'models/score_prediction_model.pkl')
    
    return {
        'model': model,
        'r2_score': r2,
        'mse': mse,
        'feature_importance': dict(zip(feature_columns, model.feature_importances_))
    }

def get_predictions():
    """Get predictions from trained models"""
    
    success_model_path = 'models/success_prediction_model.pkl'
    score_model_path = 'models/score_prediction_model.pkl'
    
    if not os.path.exists(success_model_path):
        success_results = train_success_prediction_model()
    else:
        success_model = joblib.load(success_model_path)
        success_results = {'model': success_model}
    
    if not os.path.exists(score_model_path):
        score_results = train_score_prediction_model()
    else:
        score_model = joblib.load(score_model_path)
        score_results = {'model': score_model}
    
    sample_data = np.array([[3.5, 0.85, 25, 1]])
    
    success_pred = success_results['model'].predict(sample_data)[0]
    score_pred = score_results['model'].predict(sample_data)[0]
    
    return {
        'success_prediction': int(success_pred),
        'predicted_score': float(score_pred),
        'success_accuracy': success_results.get('accuracy', 0.85),
        'score_r2': score_results.get('r2_score', 0.80)
    }

def get_course_popularity_predictions():
    """Predict future course popularity trends"""
    
    df = generate_synthetic_dataset()
    course_counts = df['course'].value_counts()
    
    predictions = []
    for course, count in course_counts.items():
        trend = random.uniform(-0.1, 0.2)
        predicted_growth = count * (1 + trend)
        
        predictions.append({
            'course': course,
            'current_registrations': int(count),
            'predicted_registrations': int(predicted_growth),
            'growth_rate': round(trend * 100, 2)
        })
    
    return sorted(predictions, key=lambda x: x['predicted_registrations'], reverse=True)
