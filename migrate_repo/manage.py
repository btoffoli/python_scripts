#!/usr/bin/env python
from migrate.versioning.shell import main

if __name__ == '__main__':
    main(url='postgresql://geocontrol:geo007@localhost:25433/teste1', debug='False', repository='.')
