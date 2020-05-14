#!/bin/bash
set -e

pytest --ckan-ini=subdir/test.ini --cov=ckanext.showcase ckanext/showcase/tests
