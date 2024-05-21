# Philadelphia Councilmatic

Based on the [Datamade Starter Template](https://github.com/datamade/councilmatic-starter-template)

The council scraper and the django site work well, but not perfectly. There are still a few loose bolts and rough edges, so if you try it out, keep that in mind. 

It may be that some amount of manual tending is necessary for this app to work exactly right. There are many odd things that happen with legilsative data. A Council Person's name may be spelled with a ' character sometimes and a smart-quote other times, for example, or misspelled, or with or without middle names, or many other odd variations that software would have a hard time keeping up with. 


## Running in development

Load env variables with `source .env`.

Collect recent legislation with `pupa update philadelphia_scraper`

Start an elasticsearch container with `docker-compose up`.

Build the elasticsearch index with `./manage.py update_index`. 

Start the development server with `./manage.py runserver`.

Enjoy learning about Philadelphia's City Council from the comfort of your localhost!

## Running in production







Copyright (c) 2019 Participatory Politics Foundation and DataMade. Released under the [MIT License](https://github.com/datamade/councilmatic-starter-template/blob/master/LICENSE).
