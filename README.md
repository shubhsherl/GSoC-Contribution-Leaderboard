
# Rocket.Chat GSoC Contributions Leaderboard

![Rocket.Chat GSoC Contributions Leaderboard screenshot](https://github.com/Sing-Li/bbug/blob/master/images/leaderboard.png)

See your position on leaderboard based on the Commits, Issues and PRs, submitted by you across the repositories of Rocket.Chat (or other GSoC organization).

Happy Coding.

## Running the Project Locally

First, clone the repository to your local machine:

```bash
git clone https://github.com/shubhsherl/RC_leaderboard.git
```

Install the requirements:

```bash
pip install -r requirements.txt  #build in python3
```

Add your Github Auth Token in `RC_leaderboard/setting.py`

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

