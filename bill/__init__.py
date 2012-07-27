# -*- coding: utf-8 -*-
from flask import Flask
import settings

app = Flask("bill")
app.config.from_object("bill.settings")

import views

