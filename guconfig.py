# -*- coding: utf-8 -*-
"""
Created on Fri Dec  5 13:18:34 2025

@author: Acer
"""

bind = '0.0.0.0:6173'
workers = 9
wsgi_app = 'app:app'
accesslog = '-'
errorlog = '-'