![logo](https://cloud.githubusercontent.com/assets/109988/12101478/fb48694c-b302-11e5-8ff5-0a607bf7c848.png)

`elex-admin` is a lightweight, Flask-based CRUD admin for election results data loaded with [elex-loader](https://github.com/newsdev/elex-loader) and [elex](https://github.com/newsdev/elex).

![admin screenshot](https://cloud.githubusercontent.com/assets/109988/12132936/acc0491a-b3ee-11e5-9563-fa7583b83c8d.png)

## Getting started
* Set up software and environment.
```
git clone git@github.com:newsdev/elex-admin.git && cd elex-admin
mkvirtualenv elex-admin
pip install -r requirements.txt
```

* This project requires [Adcom](https://github.com/newsdev/adcom) for its theme. You can deploy Adcom to a CDN like Amazon S3 and then specify the root of the URL in an environment variable.
```
export ELEX_ADMIN_CDN_URL=http://my.cdn.url.s3.amazonaws.com/cdn
```

* Run `bootstrap.sh`, `init.sh` and `update.sh` from [elex-loader](https://github.com/newsdev/elex-loader).

* Run the admin.
```
python -m elex_admin.app
```

## Interface

#### Select a race.
![screen shot 2016-01-04 at 4 58 56 pm](https://cloud.githubusercontent.com/assets/109988/12101773/7ca59c98-b304-11e5-8384-52cf9bf39584.png)

#### Edit candidate names and metadata.
![screen shot 2016-01-04 at 4 54 19 pm](https://cloud.githubusercontent.com/assets/109988/12101644/d7b9fd3c-b303-11e5-8c0c-415b5b8b5946.png)