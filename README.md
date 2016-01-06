![logo](https://cloud.githubusercontent.com/assets/109988/12101478/fb48694c-b302-11e5-8ff5-0a607bf7c848.png)

`elex-admin` is a lightweight, Flask-based CRUD admin for election results data loaded with [elex-loader](https://github.com/newsdev/elex-loader) and [elex](https://github.com/newsdev/elex).

## Interface

#### Select a race.
![select a race](https://cloud.githubusercontent.com/assets/109988/12133006/376af38a-b3ef-11e5-9879-27b6236768b8.png)

#### Edit race and candidate metadata.
![edit race detail](https://cloud.githubusercontent.com/assets/109988/12132936/acc0491a-b3ee-11e5-9563-fa7583b83c8d.png)


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