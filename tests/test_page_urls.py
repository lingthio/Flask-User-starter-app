# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>

from __future__ import print_function   # Use print() instead of print
from flask import url_for

def test_page_urls(client):
    # Visit home page
    response = client.get(url_for('home_page'))
    assert b'<h1>Home page</h1>' in response.data
    
    # Login as member and visit Member page
    response = client.post(url_for('user.login'), follow_redirects=True,
            data=dict(username='member', password='Password1'))
    assert b'<h1>Home page</h1>' in response.data
    response = client.get(url_for('member_page'))
    assert b'<h1>Member page</h1>' in response.data

    # Edit User Profile page
    response = client.get(url_for('user_profile_page'))
    assert b'<h1>User Profile</h1>' in response.data
    response = client.post(url_for('user_profile_page'), follow_redirects=True,
            data=dict(first_name='Member', last_name='User'))
    response = client.get(url_for('member_page'))
    assert b'<h1>Member page</h1>' in response.data

    # Logout
    response = client.get(url_for('user.logout'), follow_redirects=True)
    assert b'<h1>Home page</h1>' in response.data

    # Login as admin and visit Admin page
    response = client.post(url_for('user.login'), follow_redirects=True,
            data=dict(username='admin', password='Password1'))
    assert b'<h1>Home page</h1>' in response.data
    response = client.get(url_for('admin_page'))
    assert b'<h1>Admin page</h1>' in response.data

    # Logout
    response = client.get(url_for('user.logout'), follow_redirects=True)
    assert b'<h1>Home page</h1>' in response.data
