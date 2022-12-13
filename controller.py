import flask
from flask import render_template, request
import requests
import datasource
import populateDatabase
import sys

app = flask.Flask(__name__)

# This line tells the web browser to *not* cache any of the files.
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Usage: {0} host port'.format(sys.argv[0]), file=sys.stderr)
        exit()
    
    
    creator = populateDatabase.externalDataCollector()
    creator.populateDatabaseWithBattles()

    host = sys.argv[1]
    port = sys.argv[2]
    app.run(host=host, port=port)