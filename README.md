# Tuning Driver Library in Python

***With YAML specification***

## Overview

* Handle tuning space specified in YAML file
    * Build graph
    * Generate tuning space with path definition
* Handle tuning runs and reporting

## Structure

* `tspec/loader.py`: YAML handling and graph generation
* `tspec/search`: Search strategies
* `tspec/reporter`: Report mechanics
* `examples`: Some examples, YAML and corresponding python driver

## Getting started

* Setup (recommended in virtual environment): `python setup.py develop`
* Run examples
