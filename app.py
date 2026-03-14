from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os

def now():
    return datetime.utcnow()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mushroom_lab.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Stage delays in days
STAGE_DELAYS = {
    'culture': 7,
    'lc': 7,
    'spawn': 14,
    'blocks': 18
}

class Batch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    current_stage = db.Column(db.String(20), default='culture')
    
    stage_events = db.relationship('StageEvent', backref='batch', lazy=True, cascade='all, delete-orphan')
    tasks = db.relationship('Task', backref='batch', lazy=True, cascade='all, delete-orphan')

class StageEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('batch.id'), nullable=False)
    stage = db.Column(db.String(20), nullable=False)
    event_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('batch.id'), nullable=False)
    task_type = db.Column(db.String(50), nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def generate_next_stage_task(batch, current_stage):
    """Generate task for next stage based on current stage completion"""
    stage_order = ['culture', 'lc', 'spawn', 'blocks']
    current_index = stage_order.index(current_stage)
    
    if current_index < len(stage_order) - 1:
        next_stage = stage_order[current_index + 1]
        delay_days = STAGE_DELAYS[current_stage]
        due_date = datetime.utcnow() + timedelta(days=delay_days)
        
        task = Task(
            batch_id=batch.id,
            task_type=f"{next_stage.title()} Inoculation",
            due_date=due_date
        )
        db.session.add(task)
        db.session.commit()

@app.route('/')
def dashboard():
    today = datetime.utcnow().date()
    today_tasks = Task.query.filter(
        Task.due_date <= today,
        Task.completed == False
    ).order_by(Task.due_date).all()
    
    batches = Batch.query.order_by(Batch.created_at.desc()).all()
    
    return render_template('dashboard.html', 
                         today_tasks=today_tasks, 
                         batches=batches)

@app.route('/batch/new', methods=['GET', 'POST'])
def new_batch():
    if request.method == 'POST':
        name = request.form['name']
        batch = Batch(name=name)
        db.session.add(batch)
        db.session.commit()
        
        # Generate first task for culture inoculation
        task = Task(
            batch_id=batch.id,
            task_type="Culture Inoculation",
            due_date=datetime.utcnow()
        )
        db.session.add(task)
        db.session.commit()
        
        flash(f'Batch "{name}" created successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('new_batch.html')

@app.route('/batch/<int:batch_id>')
def view_batch(batch_id):
    batch = Batch.query.get_or_404(batch_id)
    stage_events = StageEvent.query.filter_by(batch_id=batch_id).order_by(StageEvent.event_date.desc()).all()
    tasks = Task.query.filter_by(batch_id=batch_id).order_by(Task.due_date).all()
    
    return render_template('view_batch.html', 
                         batch=batch, 
                         stage_events=stage_events, 
                         tasks=tasks)

@app.route('/batch/<int:batch_id>/record_stage', methods=['POST'])
def record_stage(batch_id):
    batch = Batch.query.get_or_404(batch_id)
    stage = request.form['stage']
    notes = request.form.get('notes', '')
    
    # Create stage event
    event = StageEvent(
        batch_id=batch_id,
        stage=stage,
        notes=notes
    )
    db.session.add(event)
    
    # Update batch current stage
    batch.current_stage = stage
    
    # Generate next stage task
    generate_next_stage_task(batch, stage)
    
    db.session.commit()
    
    flash(f'{stage.title()} stage recorded for batch "{batch.name}"', 'success')
    return redirect(url_for('view_batch', batch_id=batch_id))

@app.route('/task/<int:task_id>/complete', methods=['POST'])
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = True
    task.completed_at = datetime.utcnow()
    db.session.commit()
    
    flash('Task marked as completed!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/pipeline')
def pipeline_status():
    batches = Batch.query.order_by(Batch.created_at.desc()).all()
    
    pipeline_data = []
    for batch in batches:
        stage_events = StageEvent.query.filter_by(batch_id=batch.id).order_by(StageEvent.event_date).all()
        stages_completed = [event.stage for event in stage_events]
        
        pipeline_data.append({
            'batch': batch,
            'stages_completed': stages_completed,
            'pending_tasks': Task.query.filter_by(batch_id=batch.id, completed=False).count()
        })
    
    return render_template('pipeline.html', pipeline_data=pipeline_data)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
