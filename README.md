# GDPRLocationAnonymiser
Anonymise locations to comply with GDPR.

*Under development!

Developed with Python 3.7, should work for Python 3.6+.

## Usage

```
>> python .\grid_anonymiser.py -h
usage: grid_anonymiser.py [-h] -f <path-to-file> [-n <n_systems>]
                          [-t <n_systems>]

Determine optimal grid required to anonymise locations.

optional arguments:
  -h, --help            show this help message and exit
  -f <path-to-file>, --infile <path-to-file>
                        Specify a CSV file containing id,lon,lat co-ordinates
                        (one pair of co-ordinates per line) with headerline
                        'id,longitude,latitude'.
  -n <n_systems>, --number <n_systems>
                        Specify the minimum number of systems per grid square
                        to achieve anonymisation (defaults to 3).
  -t <n_systems>, --tolerance <n_systems>
                        Specify the number of systems that can be discarded in
                        order to achieve smaller grid size.
```
