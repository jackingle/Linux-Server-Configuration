from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, School, Spell, User
from flask import session as login_session
import random
import string
import os
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
"""
Throughout the code app.route() decorator appears which binds functions to a
URL.  When the URL is accessed, the function runs.
"""

"""
This makes an object of the Flask class.
"""
app = Flask(__name__)
"""
This loads a json with oauth2 related information for google.
"""
PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(PROJECT_ROOT, 'client_secrets.json')
CLIENT_ID = json.load(open(json_url))['web']['client_id']
#with app.open_resource('client_secrets.json') as f:
#    CLIENT_ID = json.load(f)['web']['client_id']
 #  CLIENT_ID = json.loads(
 #   open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog"
"""
The code block below creates an engine tied to the database and binds a mapper
to sessions.  The ?check_same_thread=False option helps limit the reuse of
threads.
"""
engine = create_engine('postgresql://catalog:catalog@localhost/catalog')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


"""
The functions below create an instance of the User class and then pass data
gainedthrough OAuth2 from google in the login_session object. This instance is
committed to the database in order to track the client-side user.
"""


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).all()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


"""
The function below handles the anti-forgery 'state' token which validates
that a user is who they say they are.
"""


@app.route('/login')
def showLogin():
    numTuple = '1234'
    state = numTuple
#    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
#                    for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


"""
The function below validates the token, allowing a user to use OAuth2 as
a sign-in method, currently the only sign in method for the
"""


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('home/ubuntu/Item-Catalog/client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'http://18.223.189.177.xip.io'
        print("post message"+oauth_flow.redirect_uri)
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        print("FEE FEEE")
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    print("acces token plz")
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    print("OOF")
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1].decode('utf-8'))
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print ("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
# ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'
    # see if user exists, if it doesn't make a new one
    print(data["email"])
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print ("done!")
    return output

"""
This function allows the user to disconnect from google and revokes the
access token.
"""


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print ('Access Token is None')
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print ('In gdisconnect access token is %s', access_token)
    print ('User name is: ')
    print (login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print ('result is ')
    print (result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps(
            'Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


"""
These functions provide JSON endpoints.
"""


@app.route('/school/<school_id>/spell/JSON')
def schoolMenuJSON(school_id):
    items = session.query(Spell).filter_by(
        school_id=school_id).all()
    return jsonify(Spells=[i.serialize for i in items])


@app.route('/school/<school_id>/spell/<spell_id>/JSON')
def spellJSON(school_id, spell_id):
    spell = session.query(Spell).filter_by(name=spell_id).one()
    return jsonify(spell=spell.serialize)


@app.route('/school/JSON')
def schoolsJSON():
    schools = session.query(School).all()
    return jsonify(schools=[r.serialize for r in schools])


"""
This function creates a session that queries the school database for all the
results arranged by name. This is utilized by Jinja2 to populate the site with
table data.
"""


@app.route('/')
@app.route('/school/')
def showSchools():
    schools = session.query(School).order_by(asc(School.name))
    return render_template(
        'schools.html',
        schools=schools)


"""
This function provides sessions that query the school and spell databases for
all data allowing them to be used by Jinja2.
"""


@app.route('/school/<school_id>/')
@app.route('/school/<school_id>/spell/')
def showSpell(school_id):
    school = session.query(School).filter_by(name=school_id).all()
    spells = session.query(Spell).filter_by(school_id=school_id).all()
    return render_template(
        'spells.html',
        spells=spells,
        spell_id=Spell.school_id,
        school=school,
        school_id=School.name)


"""
This function is for the specSpell page where specific spells are viewed.
"""


@app.route(
    '/school/<school_id>/spell/<spell_id>')
def specSpell(school_id, spell_id):
    spells = session.query(Spell).filter_by(name=spell_id).all()
    schools = session.query(School).filter_by(name=school_id).all()
    school_id = School.name
    spell_id = Spell.name
    return render_template(
        'specSpell.html',
        spells=spells,
        spell_id=spell_id,
        schools=schools,
        school_id=school_id)


"""
This function uses a session to create a new spell based on user inputs passed
through a form on the webpage.
"""


@app.route(
    '/school/<school_id>/spell/new/',
    methods=['GET', 'POST'])
def newSpell(school_id):
    if 'username' not in login_session:
        return redirect('/login')
    school = session.query(School).filter_by(name=school_id).all()
    if request.method == 'POST':
        newItem = Spell(
            name=request.form['name'],
            description=request.form['description'],
            user_id=login_session['user_id'],
            school_id=school_id)
        session.add(newItem)
        session.commit()
        flash('New Spell: %s Successfully Created' % (newItem.name))
        return redirect(url_for(
            'showSpell',
            school_id=school_id))
    else:
        return render_template(
            'newspell.html',
            school_id=School.name,
            school=school)


"""
This function allows a user to edit the description of a spell which is the
only field you can edit presently.
"""


@app.route(
    '/school/<school_id>/spell/<spell_id>/edit/',
    methods=['GET', 'POST'])
def editSpell(school_id, spell_id):
    if 'username' not in login_session:
            return redirect('/login')
    spells = session.query(Spell).filter_by(name=spell_id).all()
    editedSpell = session.query(Spell).filter_by(name=spell_id).one()
    creator = getUserInfo(editedSpell.user_id)
    getUserInfo(login_session['user_id'])
    if creator.id != login_session['user_id']:
        flash (
            "You cannot edit this Spell. This Spell was created by %s" % creator.name)
        return redirect(url_for('showCatalog'))
    if request.method == 'POST':
        if not request.form['description']:
            flash('Please add a description')
            return redirect(url_for(
                'specSpell',
                spell_id=Spell.name,
                school_id=Spell.school_id,
                spells=spells))
        session.query(Spell).filter_by(
            name=spell_id).update(
            {Spell.description:request.form['description']},
            synchronize_session = False)
        session.commit()
        flash('Spell Successfully Edited')
        return redirect(url_for(
            'showSpell',
            school_id=school_id))
    else:
        return render_template(
            'editSpell.html',
            spell_id=Spell.name,
            school_id=Spell.school_id,
            spells=spells)


"""
This function allows a user to delete a spell.
"""


@app.route(
    '/school/<school_id>/spell/<spell_id>/delete',
    methods=['GET', 'POST'])
def deleteSpell(school_id, spell_id):
    if 'username' not in login_session:
            return redirect('/login')
    spells = session.query(Spell).filter_by(name=spell_id).all()
    deleteSpell = session.query(Spell).filter_by(name=spell_id).one()
    school = session.query(School).filter_by(name=school_id).one()
    if request.method == 'POST':
        session.delete(deleteSpell)
        session.commit()
        flash('Spell Successfully Deleted')
        return redirect(url_for(
            'showSpell',
            school_id=school_id))
    else:
        return render_template(
            'deleteSpell.html',
            spell=deleteSpell,
            school_id=School.name,
            spell_id=Spell.name,
            spells=spells,
            school=school)


"""
This runs the program in debug mode at http://localhost:8000.
"""
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.run()
