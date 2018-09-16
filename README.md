# Tuning Driver Library in Python

***With YAML specification***

## Overview

* Handle tuning space specified in YAML file
    * Build graph
    * Generate tuning space with path definition
* Handle tuning runs and reporting (to csv/mongodb)

## Structure

* `tspec/loader.py`: YAML handling and graph generation
* `tspec/search`: Search strategies
* `tspec/reporter`: Report mechanics
* `examples`: Some examples, YAML and corresponding python driver

## Getting started

* Setup (recommended in virtual environment): `python setup.py install`
* Run examples
    * `cd examples`
    * `python quadratic.py`

## Writing tuning specification

* Tuning file start with version spec: `TSPEC: 0.01`
* Each node is defined as an YAML object such as:
~~~
compute:
    depends:
        - selectx
    scr: |
        y = x**2 - 24*x + 100
        report("y", y)
~~~
* This node is named *compute* which it is a child of *selectx*
* The *scr* (script) is a python snippet detailing the operation of the current node (such as compute the value of the quadratic function)
* *exit()* or exception in the python snippet can be used to abort computation at anytime
* *report(name, value)* can be used to log any metric.

## Tuning with specification

* Tuning run consist of 3 part:
    * The tuning specification/objective function
    * The search algorithm
    * The reporting mechanics

