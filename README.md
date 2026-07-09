# Attendance Management System

A Flask-based web application for managing student attendance at Ajeenkya DY Patil University (ADYPU), built around a master Excel workbook that tracks student details and daily attendance.

## Features

- **Batch Attendance Processing** — upload Morning & Afternoon attendance CSVs (e.g. from Zoom/Teams exports) and automatically mark students present/absent based on both sessions
- **Smart Student Matching** — matches names between the batch file and the master workbook, handling minor formatting differences, and flags ambiguous/duplicate names for manual URN resolution instead of guessing
- **Past Attendance Entry** — backdate attendance for a previous date, with the same duplicate-name resolution flow
- **Edit Attendance** — manually review and correct attendance for any date already recorded
- **Reports** — per-student attendance percentage, pie charts, and a defaulters list (below 75% attendance)
- **Auto-Recalculation** — present count, working days, and attendance % are recalculated automatically whenever attendance is updated
- **QR Code Self Check-In** *(new)* — generate a QR code valid for a short window (default 3 minutes); students scan it, verify they're on the correct campus WiFi, and submit their URN and name. Responses are capped at 2 submissions per device and automatically compiled into a downloadable Excel sheet when the window closes

## Setup

1. **Clone the repository**
   ```
   git clone <your-repo-url>
   cd AttendanceManagementSystem
   ```

2. **Create a virtual environment and install dependencies**
   ```
   python -m venv .venv
   .venv\Scripts\activate      # Windows
   pip install -r requirements.txt
   ```

3. **Set up your environment file**
   - Copy `.env.example` to `.env`
   - Set a random `SECRET_KEY` (you can generate one with `python -c "import secrets; print(secrets.token_hex(32))"`)

4. **Set up your configuration**
   - Copy `config/settings.default.json` to `config/settings.json`
   - Fill in `school_name`, `student_sheet`, `attendance_sheet`, and `date_format` to match your workbook
   - For the QR Check-In feature, set:
     - `checkin_allowed_networks` — the IP range (CIDR) of the WiFi/hotspot students must be connected to (e.g. `["10.161.186.0/24"]`)
     - `checkin_base_url` — the LAN IP and port of the machine running this app, reachable by student devices (e.g. `"http://10.161.186.197:5000"`)
     - `checkin_wifi_name` — the network name shown in the error message if a student isn't connected correctly

5. **Add your master workbook**
   - Upload your `.xlsm` file through the app's "Upload Master" page (it will be copied into `uploads/master/` and registered automatically)

6. **Run the app**
   ```
   python app.py
   ```

7. **Open your browser at**
   ```
   http://127.0.0.1:5000
   ```

## Project Structure

```
routes/             — Flask blueprints (dashboard, reports, edit, past attendance, QR check-in)
services/
  attendance/       — Processing, updating, and editing attendance
  validation/       — Batch and master workbook validation
  workbook/         — Loading and registering the master workbook
  workflow/         — Orchestrates validation + processing for a full attendance run
  reporting/        — Report and PDF generation
  checkin/          — QR check-in session management, WiFi verification, Excel export
  notification/     — (planned) SMS notifications
templates/          — HTML templates
static/             — Images, CSS, and JS assets
config/             — App settings (settings.json is gitignored — see Setup)
models/             — Shared data models (e.g. validation results)
utils/              — Constants and logging
```

## Notes

- `config/settings.json`, `.env`, and everything under `uploads/` are gitignored since they contain real student data and machine-specific configuration. Use `settings.default.json` and `.env.example` as your starting templates.
- The QR Check-In feature relies on students being on the *same local network* as the machine running the app — it verifies this via IP address range, since browsers cannot read WiFi network names directly. Update `checkin_allowed_networks` whenever the hosting network changes.
- Check-in responses are stored in memory for the duration of the session (default 3 minutes) and exported to Excel — they are not saved permanently, so download them before the app restarts.

## Future Improvements

- SMS & Email attendance notifications
- Persistent storage for check-in sessions (currently in-memory only)