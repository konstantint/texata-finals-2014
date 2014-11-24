Texata 2014 Finals Solution
===========================
*Konstantin Tretyakov, 23.11.2014, Austin, TX*

The following is a set of files presented as a solution to the final event of the Texata Big Data Championship 2014.
Some minor cleaning up of the explanatory texts was done after the event, but in general this is largely the solution as is.

The solution consists of some Python code, given in the `tx/` package, and a set of IPython notebooks (the `.ipynb` files).
In order to view the ipython notebooks, you need to install `ipython` and launch
 
    $ ipython notebook
    
from this directory. The HTML exports of the notebooks are in the `html/` directory, those can be viewed without the need
to install anything. It is impossible to re-run most of the code because the Cisco data provided for the contest is not publicly available, 
anyway (although most, if not all, of it was a public scrape from the web).

Toolset
=======
The following commands would install (in Debian or Ubuntu) the most relevant of the packages that I had installed for the contest (not all of them turned out necessary):

    $ sudo apt-get install -y python-numpy python-scipy python-matplotlib python-lxml \
                              python-pandas python-pandas-lib python-sklearn \
                              python-sklearn-doc python-sklearn-lib python-nltk \
                              python-tables python-tables-lib python-pip \
                              python-virtualenv ipython ipython-notebook \
                              python-pygments python-sphinx python-pydot \
                              python-pytest python-dateutil python-zmq \
                              python-networkx python-requests \
                              python-sqlalchemy python-psycopg2
    $ sudo apt-get install unzip git awscli screen pandoc
    $ sudo pip install textblob
    $ python -m textblob.download_corpora

In addition, I used a PostgreSQL server to manage the data:

    $ apt-get install postgresql-9.3 postgresql-client-9.3

Some of the experiments use [data from StackOverflow](https://archive.org/details/stackexchange), imported using [StackExchangeImporter](https://github.com/1123/StackExchangeImporter). I had it at my disposal way before the contest.

Preparation
===========
The contest is only 4 hours long, some preparation was done on the two evenings before it (essentially providing somewhere around 4 + 4 additional hours). 
So, to make it clear:

 * Data model in `tx.db_so` stems from my personal codebase from before the contest.
 * `tx.features`, `tx.hash` and `tx.similarity` is my own previous work, minor parameter tuning and code cleaning went in before and during the contest.
 * `tx.tagging`, together with notebooks `2`, `4` and `5` were written on Friday/Saturday evenings before the contest.
 * Data importing code in `tx.db` was prepared on Saturday evening before the contest, after we were given the sample data files.
 * The first two paragraphs of notebook `1` were also written down on Saturday evening.
 * The rest of `1`, as well as `3` and `6` were created using the actual data during the contest. A lot of time during the contest went into preparing the presentation slides as well.

Parallelization
===============
Although we were not allowed to use external servers during the contest, the SO tagging models were created on the previous evening without Cisco data.
For those I could use a set of additional 32 IPython "engines" on a 32-core machine from AWS. This greatly reduces the wait time to get the results interactively. Note that an easy way to start such a cluster is via the [`starcluster` tool](http://star.mit.edu/cluster/) with its `ipython_plugin`.

License
===============
The code in this repository is free for reuse in accordance with the MIT license. The text in README and notebooks is CC-BY-SA.