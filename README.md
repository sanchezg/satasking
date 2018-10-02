# satasking
Simulation of tasking between a master GroundStation and different Satellite clients.

# Installation

Install git and clone this repo. Install Python3 and Pip, then:
```
  $ pip install -r requirements.txt
```

For better results, use [pyenv](https://github.com/pyenv/pyenv) and [virtualenv](https://github.com/pyenv/pyenv-virtualenv).

# Using guide

Run the GroundStation emulator with:
```
  $ python ground-station.py [--host <HOST>] [--port <PORT>]
```

If they are not specified, by default, `HOST = 127.0.0.1` and `PORT = 65265`.

In other terminals, run as many Satellite emulator as you want:
```
  $ python satellite.py [--host <HOST>] [--port <PORT>] [-r <R>]
```
