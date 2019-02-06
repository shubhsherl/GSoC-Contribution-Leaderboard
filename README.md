# RC_leaderboard

Rocket.Chat Leaderboard for GSoC aspirants. Register yourself and see
your position on leaderboard based on the commits and PRs, submitted by
you on any repo of Rocket.Chat.

Happy Coding.

## Running the Project Locally

First, clone the repository to your local machine:

```bash
git clone https://github.com/shubhsherl/RC_leaderboard.git
```

Install the requirements:

```bash
pip install -r requirements.txt
```

*PS: If you have issues installing either `gunicorn` or `psycopg2`, you can remove them from the requirements.txt file and run the command again.*

Create the database:

```bash
python manage.py migrate
```

Finally, run the development server:

```bash
python manage.py runserver
```

## Admin Setup

First, create a super User:

```bash
python manage.py createsuperuser
```

Run the project, and open admin({url}/admin) page:

Login using the created superuser.

Add/Remove user to GSoC list using action in Core>Users.

The project will be available at **127.0.0.1:8000**.

