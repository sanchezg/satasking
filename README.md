# satasking
Simulation of tasking between a master GroundStation and different Satellite clients.

This project uses a simple backend in Django to serve the `GroundStation`, `Satellite` and `Task` models. Once executed, you can add a GroundStation instance and run it, and as many Satellite instances as you want, and run them.

Once executed the GroundStation instance, it will run a Python SocketServer in background, listening to Satellite (clients) connections. In the other hand, Satellite instances run Python socket clients, and they try to connect to listening SocketServer.

Also you can create as many Task instances as you want, and they can be selected and dispatched to be executed by clients. The GroundStation uses a kind of greedy choice algorithm (similar to fractional knapsack problem) to select which Task will be executed and maximize the result payoff.

# Installation

Install git and clone this repo. Install Python3 and Pip, then:
```
  $ pip install -r requirements.txt
```

For better results, use [pyenv](https://github.com/pyenv/pyenv) and [virtualenv](https://github.com/pyenv/pyenv-virtualenv).

## Backend settings

1. Configure the backend settings by running migrations:

```
  satasking/simulator/ $ python manage.py migrate
```

2. Create a user:

```
  satasking/simulator/ $ python manage.py createsuperuser
```

# Using guide

1. Run the django web server with:

```
  satasking/simulator/ $ python manage.py runserver
```

This will run the project under `http://localhost:8000/`

2. Go to `http://localhost:8000/admin` web interface and create a new `GroundStation` instance, and many `Satellite` instances as you want.
 
In all cases, if they are not specified, by default `HOST = 127.0.0.1` and `PORT = 65265`.

3. Create as many `Task` instances as you want.
4. Run the created instances, and dispatch the tasks.
