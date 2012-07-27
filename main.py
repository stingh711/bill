# -*- coding: utf-8 -*-

from bill import app

app.run(host='0.0.0.0')
#from gevent.wsgi import WSGIServer

#server = WSGIServer(('172.25.21.22', 8080), app)
#server.serve_forever()
