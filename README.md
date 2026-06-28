# Attendance Management System

A Flask-based web application for managing student attendance.

## Features
- Process morning & afternoon batch attendance from CSV files
- Auto-match student names (handles swapped first/last names)
- Edit past attendance
- Add attendance for past dates
- Reports with pie chart per student
- Defaulters list (below 75%)
- Auto-recalculates present count, working days & attendance %

## Setup

1. Clone the repository

2. Install dependencies
   pip install -r requirements.txt

3. Add your master workbook
   - Place your .xlsm file in uploads/master/
   - Update config/settings.json with the correct filename

4. Run the app
   python app.py

5. Open browser at
   http://127.0.0.1:5000

## Project Structure
- routes/        — Flask blueprints
- services/      — Business logic
- templates/     — HTML templates
- static/        — Images and assets
- config/        — Settings
- models/        — Data models
- tests/         — Test scripts

## Future Improvements
- SMS & Email Updates.
