# 🍄 Mushroom Lab Production Pipeline

A web application for managing mushroom cultivation production batches with automated task scheduling based on growth stage delays.

## Features

- **Batch Management**: Create and track mushroom production batches
- **Stage Tracking**: Monitor progress through 5 growth stages (Culture → LC → Spawn → Blocks → Harvest)
- **Automated Task Generation**: Tasks are automatically created based on stage completion with proper delays
- **Dashboard**: View today's tasks and recent batches at a glance
- **Pipeline Overview**: See all batches in the pipeline with their current status

## Production Stages & Delays

1. **Culture** → 7 days → **LC** 
2. **LC** → 7 days → **Spawn**
3. **Spawn** → 14 days → **Blocks** 
4. **Blocks** → 18 days → **Harvest**

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and navigate to `http://localhost:5000`

## Usage

1. **Create a New Batch**: Click "New Batch" and give your batch a name
2. **Record Stage Events**: As you complete each stage, record it in the batch details
3. **Complete Tasks**: When tasks appear on your dashboard, mark them as complete
4. **Monitor Pipeline**: Use the Pipeline Status page to see all batches at once

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite
- **Frontend**: HTML with inline CSS
- **Task Scheduling**: Automated based on stage completion dates

## File Structure

```
trametes/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── mushroom_lab.db    # SQLite database (created automatically)
└── templates/
    ├── dashboard.html    # Main dashboard view
    ├── new_batch.html    # Create new batch form
    ├── view_batch.html   # Batch details and stage recording
    └── pipeline.html     # Pipeline overview
```

## Database Schema

- **Batch**: Production batch information
- **StageEvent**: Records of completed stages
- **Task**: Automated tasks with due dates