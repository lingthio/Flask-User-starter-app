# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>

from __future__ import print_function  # Use print() instead of print
from flask import url_for


def test_page_urls(client):
    # Visit home page
    response = client.get(url_for('home_page'))
    assert b'<h1>Home page</h1>' in response.data

    # Login as user and visit User page
    response = client.post(url_for('user.login'), follow_redirects=True,
                           data=dict(email='user@example.com', password='Password1'))
    assert b'<h1>Home page</h1>' in response.data
    response = client.get(url_for('user_page'))
    assert b'<h1>User page</h1>' in response.data

    # Edit User Profile page
    response = client.get(url_for('user_profile_page'))
    assert b'<h1>User Profile</h1>' in response.data
    response = client.post(url_for('user_profile_page'), follow_redirects=True,
                           data=dict(first_name='User', last_name='User'))
    response = client.get(url_for('user_page'))
    assert b'<h1>User page</h1>' in response.data

    # Logout
    response = client.get(url_for('user.logout'), follow_redirects=True)
    assert b'<h1>Home page</h1>' in response.data

    # Login as admin and visit Admin page
    response = client.post(url_for('user.login'), follow_redirects=True,
                           data=dict(email='admin@example.com', password='Password1'))
    assert b'<h1>Home page</h1>' in response.data
    response = client.get(url_for('admin_page'))
    assert b'<h1>Admin page</h1>' in response.data

    # Logout
    response = client.get(url_for('user.logout'), follow_redirects=True)
    assert b'<h1>Home page</h1>' in response.data
