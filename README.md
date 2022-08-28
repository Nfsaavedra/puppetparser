# puppetparser

puppetparser is a Python library to parse Puppet scripts. This parser allows the transformation of a Puppet script into an object model that represents the constructs of the Puppet DSL language.

## Installation

To install run:
```
pip install puppetparser
```

Or clone the Github repository and run:
```
python3 setup.py install
```

## Usage


```python
from puppetparser.parser import parse

with open(path) as f:
    parsed_script, comments = parse_puppet(f.read())
```

## Tests

To run the tests:
```
python3 -m unittest discover tests
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[GPL-3.0](https://choosealicense.com/licenses/gpl-3.0/)
