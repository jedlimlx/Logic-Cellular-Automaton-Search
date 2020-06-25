I've been working on this program for a few days now. I would like to thank Mateon1 for helping me with CNF and debugging and WildMyron for the original idea.

Installation
------------
LCAS depends on PySAT and requires Python 3.6 or higher.

If you're on Windows 10 and already have Python 3 installed, run "pip install python-sat" in your cmd.
If you don't already have Python 3 try using WSL.

If that doesn't work (it probably won't) or you are on Linux, go to Windows Subsystems for Linux (if you are on Windows 10)
Run these commands:
``sudo apg-get update
sudo apt-get install python3.6-dev
sudo apt install python3-pip
sudo apt-get install zlib1g-dev
pip3 install python-sat```

Don't be alarmed if there are warnings produced by "pip3 install python-sat". Just let it run to completion.

To use the application, run
```python main.py -p <period> -dx <displace_x> -dy <displace_y> -x <bound_x> -y <bound_y>```

Run
```python main.py --help```
for more options

The rule format is the same as CAViewer's rule.ca_rule format. You will need to specify a rule file with the relevant rule to run the program. If no rule is specified it defaults to rule.ca_rule.

Features
-----------
* Support for alternating HROT rules
* Automatic generation of pattern files for spaceship searches
* Support for C1 symmetry
* Support for Glucose4, Glucose3, Lingeling, Cadical, Minisat and MapleSAT

TODO
----------
* Partial rules
* Isotropic Non-Totalistic Rules
* Anisotropic Non-Totalistic Rules
* Multistate Rules

Speed
------------
Finds the following ship in R2,C2,S2,7,12,B3,8,NN in a 7x7 bounding box in 34s (Cadical), 17s (Minisat), 79s (Glucose4)
```
x = 18, y = 16, rule = R2,C2,S2,7,10,B3,8,NN
..................$
..................$
..................$
..................$
..................$
..................$
........o.o.......$
.....oo...oo......$
..................$
.........o........$
..................$
..................$
..................$
..................$
..................$
..................$
```

Finds the c/5o in Minibugs in 16 mins on C1 search with Glucose4
```
x = 13, y = 15, rule = R2,C2,M0,S6..9,B7..8,NM
.............$
.............$
.............$
.............$
.............$
.............$
.....ooo.....$
....o...o....$
....oo.oo....$
.....ooo.....$
.............$
.............$
.............$
.............$
.............$
```