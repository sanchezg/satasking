# satasking
Simulation of tasking between a master GroundStation and different Satellite clients.

This project uses a simple backend in Django to serve the `GroundStation`, `Satellite` and `Task` models. Once executed, you can add a GroundStation instance and run it, and as many Satellite instances as you want, and run them.

Once executed the GroundStation instance, it will run a [Python SocketServer](https://docs.python.org/3/library/socketserver.html#server-objects) in background, listening to `Satellite` (clients) connections. In the other hand, `Satellite` instances run [Python socket](https://docs.python.org/3/library/socket.html#socket-objects) clients, and they try to connect to listening `SocketServer`.

Also you can create as many `Task` instances as you want (Task takes unique names, a payoff and the resources), and they can be selected and dispatched to be executed by clients. The `GroundStation` uses a kind of [greedy choice algorithm](https://en.wikipedia.org/wiki/Continuous_knapsack_problem) (similar to fractional knapsack problem) to select which `Task` will be executed and maximize the result payoff.

Here, the satellites are supposed to be multitasking: they can receive several tasks and begin their execution instantly, the only constraint is that received tasks don't compete by resources.

Each satellite "throw a dice" each time a new task arrives to determine if the task will be executed: it raises an error the 10% of time, noticing that the task couldn't be executed.

Once logged in, the API serves the following endpoint: `http://localhost:8000/api/taskexecution/` with all detailed information of task dispatching between the groundstation and the client.

**Note 1**: As this is a very first version, it is mandatory to stop satellite clients **before** stopping the groundstation server. Otherwise it could hang the django server.

**Note 2**: There are a lot of `TODO` commented in the code, they are addressing improval opportunities or technical debt (in some cases).

# Installation

Install git and clone this repo. Install Python3 and Pip, then:
```
  $ pip install -r requirements.txt
```

For better results, use [pyenv](https://github.com/pyenv/pyenv) and [virtualenv](https://github.com/pyenv/pyenv-virtualenv).

## Backend settings

1. Configure the backend settings by running migrations:

```
  satasking/ $ python manage.py migrate
```

2. Create a user:

```
  satasking/ $ python manage.py createsuperuser
```

3. Run the tests with:
```
  satasking/ $ python manage.py test
```

# Using guide

1. Run the django web server with:

```
  satasking/ $ python manage.py runserver
```

This will run the project under `http://localhost:8000/`

2. Go to `http://localhost:8000/admin` web interface and create a new `GroundStation` instance, and many `Satellite` instances as you want.
 
In all cases, if they are not specified, by default `HOST = 127.0.0.1` and `PORT = 65265`.

3. Create as many `Task` instances as you want.
4. Run the created instances, and dispatch the tasks.
