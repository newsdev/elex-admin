![logo](https://cloud.githubusercontent.com/assets/109988/12101478/fb48694c-b302-11e5-8ff5-0a607bf7c848.png)

`elex-admin` is a lightweight, Flask-based CRUD admin for election results data loaded with [elex-loader](https://github.com/newsdev/elex-loader) and [elex](https://github.com/newsdev/elex).

## Getting started
* Set up software and environment.
```
git clone git@github.com:newsdev/elex-admin.git && cd elex-admin
mkvirtualenv elex-admin
pip install -r py3.requirements.txt
```
## Add a new racedate to the admin
* Duplicate the most recent racedate.ini file in `elex_admin/`. Name it with your new racedate.
* In that file, increment the `http-socket` port by 1 (eg. `127.0.0.1:8047` -> `127.0.0.1:8048`)
* Edit `elex_admin/races.conf`: Duplicate the last `location {}` object and change the racedate and `proxy_pass` port number to match the settings in the `.ini` file you just made.
* Then run these commands:
```
workon elex-admin
fab e:stg master pull
fab e:prd master pull
```

## Running the admin
* This project requires [Adcom](https://github.com/newsdev/adcom) for its theme. You can deploy Adcom to a CDN like Amazon S3 and then specify the root of the URL in an environment variable.
```
export RACEDATE=2016-02-01
export ELEX_ADMIN_CDN_URL=http://my.cdn.url.com/cdn
```

* Run `bootstrap.sh`, `init.sh` and `update.sh` from [elex-loader](https://github.com/newsdev/elex-loader).

* Run `python elex_admin/initialize_racedate.py` to set up candidates and races for overrides.

* Run the admin.
```
python -m elex_admin.app
```
## See all races for a racedate
![screenshot](https://cloud.githubusercontent.com/assets/109988/13506676/3c69d384-e14d-11e5-898e-e2b91ba1c38d.png)

## Edit candidate information and make race calls
![screenshot](https://cloud.githubusercontent.com/assets/109988/13506720/7f125e5e-e14d-11e5-930b-d6f66008f300.png)
