# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>

from __future__ import print_function   # Use print() instead of print
from flask import url_for

def test_simple_urls(app):
    """
    Visit 'simple' URLs known to the Flask application.
    Simple URLs are URLs without default-less parameters.
    """
    # Retrieve all URLs known to the Flask application
    print('')
    for rule in app.url_map.iter_rules():
        # Calculate number of default-less parameters
        params = len(rule.arguments) if rule.arguments else 0
        params_with_default = len(rule.defaults) if rule.defaults else 0
        params_without_default = params - params_with_default

        # Skip routes with default-less parameters
        if params_without_default>0: continue

        # Skip routes without a GET method
        if 'GET' not in rule.methods: continue

        # Retrieve a browser client simulator from the Flask app
        client = app.test_client()

        # Simulate visiting the simple URL
        url = url_for(rule.endpoint)
        print('Visiting URL ' + url)
        client.get(url, follow_redirects=True)

    return