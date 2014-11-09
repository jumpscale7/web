from JumpScale import j

import mongoengine
from eve import Eve
from eve_mongoengine import EveMongoengine

from flask.ext.bootstrap import Bootstrap
from eve_docs import eve_docs

# create some dummy model class

# default eve settings
my_settings = {
    'MONGO_HOST': 'localhost',
    'MONGO_PORT': 27017,
    'MONGO_DBNAME': 'eve',
    'DOMAIN': {'eve-mongoengine': {}} # sadly this is needed for eve
}

import JumpScale.grid.osis

client = j.core.osis.getClientByInstance('main')
json=client.getOsisSpecModel("oss")

from generators.MongoEngineGenerator import *

gen=MongoEngineGenerator("generated/oss.py")
gen.generate(json)

# init application
app = Eve(settings=my_settings)
# init extension
ext = EveMongoengine(app)
# register model to eve

from generated.oss import *

for classs in classes:
    ext.add_model(classs)

Bootstrap(app)
app.register_blueprint(eve_docs, url_prefix='/docs')

print "visit:\nhttp://localhost:5000/docs/"

# let's roll
app.run()