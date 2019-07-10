
CONTENTS OF THIS FILE
---------------------

 * Introduction
 * Location
 * Technologies
 * Recommended plugins
 * Requirements
 * Tests
 * Configuration
 * Author

INTRODUCTION
------------

The "log_parser.py"- python 3 script to parse ngnix logs.

LOCATION
---------

- SSH: git@gitlab.com:AShipulin/pythondev.git
- HTTPS: https://gitlab.com/AShipulin/pythondev.git

TECHNOLOGIES
-------------

Used only Python standard libraries.

RECOMMENDED PLUGINS
-------------------

- .gitignore - prevents redundant uploads.
- GitLab - projects integration with remote repo.

REQUIREMENTS
------------

1. PyCharm IDEA installed.
2. Python 3.6 or later installed.
3. Python virtualenvironment installed out of the project and activated.
4. Python interpreter configured.

TESTS
-----

1 Run all tests:
* $ pytest -v 

2 Run tests as a package:
* $ pytest -v 

CONFIGURATION
--------------

- Parse default configuration defined as config dictionary inside the log_parser.py.

- To pass custom configuration use command line option -p (--path) with path to json config.


AUTHOR
-----------

* Anton Shipulin <antishipul@yandex.ru> 
