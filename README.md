# eazee-parking (vehicle-parking-app V1)
<hr>
##Student Information:
- Name: Himanshu Rastogi
- Roll Number: 22f2001665
- Email Id: 22f2001665@ds.study.iitm.ac.in

### About Me
- I’m a second-year Data Science and Programming student at IIT Madras. I am very interested in learning programming and choosing between tradeoff is one my favourite task. This project make me learn a lot and I have tried my best to make as good as I can.
<hr>

## Project Description:
This project targets to create a nice web app, which can be used to book parking spots by users and also gives admin an easy access to maintain the lots and users.


## Overview

This project is a Flask-based web application for managing parking lots, users, reservations, and admin operations. It uses SQLAlchemy for ORM, Flask-Login for authentication, and organizes code using Blueprints for modularity.

---

## Project Structure

```
app.py
application/
    __init__.py
    config.py
    extensions.py
    admin/
        __init__.py
        admin_forms.py
        routes.py
    auth/
        __init__.py
        forms.py
        routes.py
    database/
        __init__.py
        init_db.py
        models.py
    main/
        __init__.py
        routes.py
    user/
        __init__.py
        routes.py
        user_forms.py
```

## 📊 Entity Relationship Diagram (ERD)

![ERD](/erd.png)


---

## Main Python Files

### app.py
- **Purpose:** Entry point for the Flask app. Registers CLI commands for seeding, clearing, and dropping the database.
- **Key Functions:**  
  - `seed`: Populates the database with sample data.
  - `clear_data`: Clears all data from tables.
  - `drop_all`: Drops all database schemas.
  - `flask run` or `python app.py` will run the app.

### application/__init__.py
- **Purpose:** Application factory and blueprint registration.
- **Key Functions:**  
  - `create_app`: Initializes Flask app, configures extensions, registers blueprints.
  - `load_user`: Loads user for Flask-Login.

### application/config.py
- **Purpose:** Contains configuration classes for different environments.

### application/extensions.py
- **Purpose:** Initializes Flask extensions (e.g., SQLAlchemy, LoginManager).

---

## Blueprints

### Admin (application/admin/)
- routes.py: Admin dashboard, lot management, summary statistics.
- admin_forms.py: WTForms for admin actions.

### Auth (application/auth/)
- routes.py: User authentication (login, logout, registration).
- forms.py: WTForms for authentication.

### User (application/user/)
- routes.py: User dashboard, reservation management, lot browsing.
- user_forms.py: WTForms for user actions.

### Main (application/main/)
- routes.py: Home and index routes.

---

## Database

### application/database/models.py
- **Purpose:** SQLAlchemy models for User, ParkingLot, ParkingSpot, Reservation.
- **Relationships:**  
  - Users can have multiple reservations.
  - ParkingLots have multiple ParkingSpots.
  - Reservations link users, lots, and spots.

### application/database/init_db.py
- **Purpose:** Functions to initialize and seed the database with sample data.

### application/database/__init__.py
- **Purpose:** Exports database models for easy import.

---

## Templates & Static Files

- Each blueprint has its own `templates/` and `static/` directories for modular HTML and css.
- Global static files are in the top-level `static/` directory.

---

## Development & Environment

- **Configuration:** Managed via `.env` and `application/config.py`.
- **Requirements:** Listed in `requirements.txt`.
- **Ignored Files:** `.gitignore` excludes compiled files, environment folders, logs, and temp files.

---

## CLI Commands

- `flask seed` – Populate the database with sample data.
- `flask clear-data` – Remove all data from the database.
- `flask drop-all` – Drop all database tables.
- `flask run` - Will run the app.
- `python app.py` Will also run the app.

---

## Getting Started

1. Install dependencies:  
   `pip install -r requirements.txt`
2. Set up environment variables in `.env`. If you don't have any then app will use the default given here.
3. Initialize the database:  
   `flask seed`
4. Run the app:  
   `python app.py`

---

## Key Modules & Classes

- `User`: User model with authentication fields.
- `ParkingLot`: Parking lot details and stats.
- `ParkingSpot`: Individual parking spots.
- `Reservation`: Reservation records linking users, lots, and spots.

---
