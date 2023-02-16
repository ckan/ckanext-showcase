# Ckanext-showcase CHANGELOG

## v1.6.0 2023-02-14

* Dropped support for CKAN 2.7 and 2.8
* Dropped support for Python 2
* Add support for CSRF token
* Sanitize blueprint names. All views should be called using `showcase_blueprint.<endpoint>`
* Rename get_showcase_wysiwyg_editor to avoid name clashes with other extensions (like `ckanext-pages`)
* Update CKEditor to it's latest version: 36.0.1

## v1.5.1 2022-08-10

* Dependency update

## v1.5.0 2022-04-20

* Support for CKAN 2.10 (#143)
* Fix message in Add to showcase button (#139)

## v1.4.8 2022-01-17

* Add Chinese (Traditional, Taiwan) translations (#136)
* Dependency update

## v1.4.7 2022-01-04

* Fix ReST in README (#133)
* Move minimal requirements into setup.py (#134)

## v1.4.6 2022-01-04

* Fix version in setup.py and add to changelog (#130)

## v1.4.5 2021-11.25

* Add German and French translations (#124, #126)
* Fix logic for API routes (#128)
* Dependency updates

## v1.4.4 2021-08-17

* Fix hardcoded route (#118)

## v1.4.3 2021-04-21

* Fix typo on setup.py (#107)


## v1.4.2 2021-04-20

* Fix ckeditor asset bundle (#105)


## v1.4.1 2021-04-08

* Fix uploads on CKAN 2.9 (71215ca)
* Upgrade CKEditor and additional libraries
* Align search form design with core (#100)
* Include webassets.yml in MANIFEST.in (#98)

## v1.4.0 2021-02-21

Features:

* Python 3 support #95
* CKAN 2.9 support #95
