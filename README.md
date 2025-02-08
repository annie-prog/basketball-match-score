
# Basketball Match RESTful API

The Basketball Match, Tournament, and League Management RESTful API is built with Flask and is designed to manage basketball matches, tournaments, and leagues. It supports a range of functionalities such as organizing events, managing tournaments and teams, and tracking results.

## 📖 Table of Contents
- [Introduction](#🌟-introduction)
- [Features](#✨-features)
- [Installation](#⚙️-installation)
- [Usage](#🚀-usage)
- [API Endpoints](#📡-api-endpoints)
- [Future Improvements](#🚧-future-improvements)
- [Contributing](#🤝-contributing)

## 🌟 Introduction
With this Flask-based tool, you can:

- Organize and manage basketball events, tournaments, and leagues.
- Support knockout (elimination) tournaments and league formats.
- Track player and team performances in matches.
- Provide user registration and role-based authentication (admin, director, user).

For a complete list of features and endpoints, refer to the [API Endpoints](#📡-api-endpoints) section.

## ✨ Features
- **Organize Sports Events**: Create and manage tournaments and matches.
- **Knockout System**: Support for knockout-style tournaments.
- **Leagues**: Create and manage leagues.
- **Player Performance Tracking**: Store and track match performance.
- **User Registration and Authentication**: Users can register, log in, and access data based on roles (admin, director, user).
  
### Additional Features:
1. **Role-based Access**:
   - Admin: Full control over tournaments, users, and data.
   - Director: Limited management rights for specific tournaments.
   - User: View-only access for results.

## ⚙️ Installation

### Prerequisites:
- Python 3.10+
- pip (Python package manager)
- PostgreSQL (for database)

### Steps:
1. Clone the repository:

```bash
git clone https://github.com/your-username/basketball-match-score.git
cd basketball-match-score
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the database

- **Install PostgreSQL**:

   Follow the installation instructions for your operating system from the official PostgreSQL website: [PostgreSQL Download](https://www.postgresql.org/download/).

- **Open pgAdmin**:

   Open **pgAdmin**, which is the graphical interface for managing your PostgreSQL databases.

- **Create the Database**:

   In **pgAdmin**, connect to your PostgreSQL server and create a new database named `basketball_matches` by running the following SQL query in the query tool:
   
   ```sql
   CREATE DATABASE basketball_matches;
   ```

- **Connect to the Database:**

    Open a terminal or command prompt and connect to your database using the following command:
    ```bash
    psql -d basketball_matches
    ```

- **Create Tables:**

    Copy and paste the provided SQL script into your PostgreSQL client (pgAdmin query tool or terminal) to create the necessary tables.

- **Verify the Setup:**

    After running the script, verify that the tables were created successfully by running the following command:
    ```bash
    \dt
    ```
    This will list all the tables in the `basketball_matches` database. You should see all the tables defined in the script.

## 🚀 Usage

### Local Execution:
You can interact with the API through the following commands:

- **Register a new user:**

```bash
curl -X POST -d "email=user@example.com&password=password" http://localhost:5000/register
```

- **Login a user:**

```bash
curl -X POST -d "email=user@example.com&password=password" http://localhost:5000/login
```

- **Create a new tournament (Admin only):**

```bash
curl -X POST -d "name=Summer League&type=Knockout" http://localhost:5000/tournaments
```

- **Retrieve all tournaments:**

```bash
curl http://localhost:5000/tournaments
```

## 📡 API Endpoints

| Method | Endpoint       | Description                                      |
|--------|----------------|--------------------------------------------------|
| POST   | /register      | Register a new user                              |
| POST   | /login         | Login to the system                              |
| GET    | /tournaments/all   | Retrieve all tournaments                         |
| GET    | /match/playerMatch       | Retrieve all player matches                             |
| GET    | /match/teamMatch       | Retrieve all team matches                             |
| POST   | /match       | Add a new match                                  |
| GET    | /player/all       | View all players                                 |
| POST   | /player       | Add a new player                                 |

## 🚧 Future Improvements
- **Automatic Scheduling**: Auto-generation of match schedules for tournaments.
- **Enhanced Statistics**: Improved tracking and analysis of player and team statistics.

## 🤝 Contributing
We welcome contributions! Please follow these steps:

1. Fork the repository.
2. Create a new branch:

```bash
git checkout -b feature/my-feature
```

3. Commit your changes and submit a pull request.
4. Ensure your code adheres to PEP 8 standards and includes appropriate documentation.

## 📧 Contact
For issues, suggestions, or feedback, feel free to open an issue or contact us directly.
