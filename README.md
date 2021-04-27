# Routine Royale

## Introduction

Routine Royale is a Battle-Royale style habit tracking application. It allows competitive competition for habit building using a Django REST Framework Web API.

## Functions
List all the functions with their sub functions of your application.
1. User Account Management
	* Create new Accounts
	* Update Account Info
2. Event Management and Interaction
	* Create Events (Public and Private)
	* Add Tasks to Events
	* Join Public Events
	* Join Private Events with an Event Key
	* View Top 5 Users in an Event
3. Task Completion and Awards
	* Complete and UnComplete Tasks in Events
	* Obtain Energy and Score from Completion and Streak
4. Graphical Interface
  * Visualize Events
  * Visualize Tasks
  * Visualize Event Participations
  * Allow Actions in Events
  * Visualize Top 5 in Events
  * Facilitate Event Creation
  * Log In and Log Out

## Getting Started
### Installation and Setup
#### Server
To run the server component of the project, the computer needs a Python interpreter with Python >= 3.8.

`sudo apt install python3.8`

In either a virtual environment or in the interpreter itself, the server needs both django and djangorestframework installed in the python interpreter.

`python3.8 -m pip install django djangorestframework`

This should allow basic access to the environment. If running the server alongside the GUI, no further configuration is needed. In production deployment, a web stack with nginx is suggested to run alongside Django.

Next, the database needs to be configured. Use Django's manage.py to apply migrations.

`manage.py migrate`

A super user account is needed for the management of the service. Use the manage script to do so.

`manage.py createsuperuser`

Next, a default Class must be created using the Admin interface, as well as the Shield and Attack. This is accessed at http://localhost:8000/admin.

#### GUI
To run the GUI component of the project, Python >= 3.8 is required, with a dependency on Kivy.

`python3.8 -m pip install kivy`

### Run
#### Server
The server can be started by running `manage.py runserver 8000`. This starts the server using the Django management console, on port 8000.

#### Client (GUI)
The GUI can be started by running `GUI_manager.py`. The GUI assumes a server running on `localhost`, but this is an easy modification to the file.

## Demo video

https://www.youtube.com/watch?v=ZR3BEtYV8sw

## Contributors

* Jordan Blackadar, jordan.blackadar@outlook.com
* Ryan Lawton, lawtonr2@wit.edu
* Ben Clermont, clermontb@wit.edu
