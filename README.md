# Pokémon PvP Teams

A web application for managing Pokémon teams in PvP formats. Users can log in, create teams, and add comments to teams. Admins have additional capabilities such as viewing all users and deleting teams.

## Features

- User authentication (Login and Signup)
- Add and view Pokémon teams
- Comment on teams
- Admin panel for user management and team deletion
- CSRF protection for forms
- Responsive design with embedded media

## Installation

To set up this project locally, follow these steps:

1. Clone the repository:
    ```bash
    git clone <repository-url>
    cd <project-directory>
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up environment variables:
    Create a `.env` file and add the following variables:
    ```env
    MY_SECRET_KEY=<your-secret-key>
    DATABASE_URI=<your-database-uri>
    FLASK_DEBUG=True
    ```

4. Initialize the database (if needed):
    ```bash
    flask db upgrade
    ```

## Usage

Run the application with:
```bash
python run.py
