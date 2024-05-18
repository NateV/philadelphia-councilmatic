# Philadelphia Councilmatic

Based on the [Datamade Starter Template](https://github.com/datamade/councilmatic-starter-template)

The council scraper and the django site work well, but not perfectly. There are still a few loose bolts and rough edges, so if you try it out, keep that in mind. 


## Running in development

Load env variables with `source .env`.

Collect recent legislation with `pupa update philadelphia_scraper`

Start an elasticsearch container with `docker-compose up`.

Build the elasticsearch index with `./manage.py update_index`. 

Start the development server with `./manage.py runserver`.

Enjoy learning about Philadelphia's City Council from the comfort of your localhost!

## Running in production







Copyright (c) 2019 Participatory Politics Foundation and DataMade. Released under the [MIT License](https://github.com/datamade/councilmatic-starter-template/blob/master/LICENSE).
