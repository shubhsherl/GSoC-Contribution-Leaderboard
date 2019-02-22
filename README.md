
# Rocket.Chat GSoC Contributions Leaderboard

![Rocket.Chat GSoC Contributions Leaderboard screenshot](https://github.com/Sing-Li/bbug/blob/master/images/leaderboard.png)

A contributions leaderboard for your GSoC organization. Students can track their position on leaderboard based on the PRs, commits, and issues they've completed across the repositories of your organization on Github.

## Benefits
- Encourage students to improve their position - by increasing contribution to your organization
- Easy to setup and administer
- Realtime organization-wide visibility to top student candidates

## Main Features
- Track commits/PRs/issues for GSoC student candidates in real time
- At a glance view of participating top students
- Easy administration to add students (even before they have made their very first contribution)

## Quick Start

Clone the repository to your local machine:

```bash
git clone https://github.com/shubhsherl/GSoC-Contribution-Leaderboard.git
```

Create a `python3` virtual environment, activate it and install the required packages
```
bash
virtualenv venv -p python3
source venv/bin/activate
pip install -r requirements.txt
```

Create a file name `.env` in the base directory (alongside manage.py) and
Add your Github Auth Token and Organization name in it as following

```
ORGANIZATION=''
GITHUB_AUTH_TOKEN=''
```

Apply database migrations
```bash
python manage.py migrate
```

Finally, run the development server

```bash
python manage.py runserver
```

To run it in background and serve on any port (eg. 3003)
```bash
nohup python manage.py runserver 0.0.0.0:3003 &
```
(For production use follow a proper method for deploying a django app in production)

To create an admin user run
```bash
python manage.py createsuperuser
```
###  Architecture

TODO: describe how django front end works briefly, and describe how the backend cron job works.
      make sure user realize that they must admin and manage an additional separate Linux cron job!

###  Starting the cron job

TODO:  add details on cron job here

#### Initiailization:  First steps

- Click on refresh at the home page to sync your db with the latest repositories from your Organization.
- Visit `/admin`, mark the Repositories from which you want to count contributions.
- Mark users as GSoC contributors under Core>Users form the admin panel.

##### Admin levels:
- **Exclude Repo:** Decide which Repo to count for LeaderBoard
- **Moderator:** The above plus the ability to add/remove users

## Description of files in Repository

Non-Python files:

filename                           |  description
----------------------------------|------------------------------------------------------------------------------------
README.md                         |  Text file (markdown format) description of the project.
requirement.txt                   |  list all packages that needs to be installed for the project.
\*.html                           |  html file for rendering web-page

Python scripts files:

filename                           |  description
----------------------------------|------------------------------------------------------------------------------------
glist.py                          |  Fetch and refresh data of GSoC candidate from the local sqlite3 database.
model.py                          |  Contains the User and Repository Model for database.
admin.py                          |  Contains the Admin Model for Administrator dashboard.
view.py                           |  Fetch data from the Github database to a local sqlite3 database.
setting.py                        |  Django file for settings of Project.


## Contributing

We welcome all contributions for any GSoC orgs, students, or community members. Feel free to contribute bug-fixes at any time. If you plan to contribute new features, utility functions or extensions, please first create an issue and discuss the feature with us. Please help us to improve our documentation, including this page!

### Some suggested  features to add
- Show details of contribution when clicked on counts
- Add `Lines Added/Deleted` stats.
- Show personalized chart of commits/issues/PRs

