from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, School, Spell, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog"

# flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
#     'client_secret.json',
#     ['openid email'])
# flow.redirect_uri = 'http://localhost:8000'

# Generate URL for request to Google's OAuth 2.0 server.
# Use kwargs to set optional request parameters.
# authorization_url, state = flow.authorization_url(
#     # Enable offline access so that you can refresh an access token without
#     # re-prompting the user for permission. Recommended for web server apps.
#     access_type='offline',
#     # Enable incremental authorization. Recommended as a best practice.
#     include_granted_scopes='true')

# Connect to Database and create database session
engine = create_engine('sqlite:///spell.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    numTuple = ('1', '2', '3', '4')
    state = ''.join(numTuple)
    # state = ''.join(random.choice(string.ascii_uppercase + string.digits)
    #     for x in range(32))
    login_session['state'] = state
    print ("help"+login_session['state'])
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    #Validate state token
    print ("Hey")
    print (login_session['state'])
    print(request.args.get('state'))
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    #Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'http://localhost:8000'
        credentials = oauth_flow.step2_exchange(code)
        print (credentials)
    except FlowExchangeError:
        print ("FlowExchangeError")
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
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

    stored_access_token = getUserID('access_token')
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
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    flash("you are now logged in as %s" % login_session['username'])
    print ("done!")
    return output

    # DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print ('Access Token is None')
        response = make_response(json.dumps('Current user not connected.'), 401)
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
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

# JSON APIs to view School Information
@app.route('/school/<int:school_id>/spell/JSON')
def schoolMenuJSON(school_id):
    school = session.query(School).filter_by(name=school_id).one()
    items = session.query(Spell).filter_by(
        school_id=school_id).all()
    return jsonify(Spells=[i.serialize for i in items])


@app.route('/school/<int:school_id>/spell/<int:spell_id>/JSON')
def spellJSON(school_id, spell_id):
    spell = session.query(Spell).filter_by(name=spell_id).one()
    return jsonify(spell=spell.serialize)


@app.route('/school/JSON')
def schoolsJSON():
    schools = session.query(School).all()
    return jsonify(schools=[r.serialize for r in schools])


# Show all schools
@app.route('/')
@app.route('/school/')
def showSchools():
    schools = session.query(School).order_by(asc(School.name))
    return render_template('schools.html', schools=schools)


# Show a spell


@app.route('/school/<school_id>/')
@app.route('/school/<school_id>/spell/')
def showSpell(school_id):
    school = session.query(School).filter_by(name=school_id).all()
    spells = session.query(Spell).filter_by(school_id=school_id).all()
    return render_template('spells.html', spells=spells, spell_id=Spell.school_id, school=school, school_id=School.name)

@app.route('/school/<school_id>/spell/<spell_id>')
def specSpell(school_id, spell_id):
    spells = session.query(Spell).filter_by(name=spell_id).all()
    schools = session.query(School).filter_by(name=school_id).all()
    return render_template('specSpell.html', spells=spells, spell_id=Spell.name, schools=schools, school_id=School.name)

# Create a new spell

@app.route('/school/<school_id>/spell/new/', methods=['GET', 'POST'])
def newSpell(school_id):
    if 'username' not in login_session:
        return redirect('/login')
    school = session.query(School).filter_by(name=school_id).all()
    if request.method == 'POST':
        newItem = Spell(name=request.form['name'], description=request.form[
                           'description'], user_id=login_session['user_id'], school_id=school_id)
        session.add(newItem)
        session.commit()
        flash('New Spell: %s Successfully Created' % (newItem.name))
        return redirect(url_for('showSpell', school_id=school_id))
    else:
        return render_template('newspell.html', school_id=School.name, school=school)

# Edit a spell


@app.route('/school/<school_id>/spell/<spell_id>/edit/', methods=['GET', 'POST'])
def editSpell(school_id, spell_id):
    if 'username' not in login_session:
            return redirect('/login')
    spells = session.query(Spell).filter_by(name=spell_id).all()
    editedSpell = session.query(Spell).filter_by(name=spell_id).all()
    school = session.query(School).filter_by(name=school_id).one()
    if request.method == 'POST':
        if not request.form['description']:
            flash('Please add a description')
            return redirect(url_for('specSpell', spell_id=Spell.name, school_id=Spell.school_id, spells=spells, school=school))
        editedSpell = Spell(description = request.form['description'])
        session.add(editedSpell)
        session.commit()
        flash('Spell Successfully Edited')
        return redirect(url_for('showSpell', school_id=school_id))
    else:
        return render_template('editSpell.html', spell_id=Spell.name, school_id=Spell.school_id, spells=spells, school=school)


# Delete a spell
@app.route('/school/<school_id>/spell/<spell_id>/delete', methods=['GET', 'POST'])
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
        return redirect(url_for('showSpell', school_id=school_id))
    else:
        return render_template('deleteSpell.html', spell=deleteSpell, school_id=School.name, spell_id=Spell.name, spells=spells, school=school)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
