from JumpScale import j

from flask import Flask, render_template, request, g, session, flash, \
     redirect, url_for, abort
from flask.ext.openid import OpenID
import ujson as json
from openid.extensions import pape

import JumpScale.baselib.hrd

# setup flask
app = Flask(__name__)

app.config['SECRET_KEY'] = 'sdsdsd'

# setup flask-openid
oid = OpenID(app, safe_roots=[], extension_responses=[pape.Response])


userhrdtemplate="""
login=
email=
name=
alias=,
company=,
skype=,
mobile=,
jabber=,
openid=,
"""

grouphrdtemplate="""
members=,
"""


class UserManagerHRD():
    def __init__(self,subdir=""):
        self.users={}
        self.groups={}
        self.openidToUserId={}
        self._hrddir="%s/hrd/%s"%(j.system.fs.getcwd(),subdir)
        j.system.fs.createDir(self._hrddir)
        self.load(True)

    def load(self,userinit=False):
        self.hrd=j.core.hrd.getHRD(self._hrddir,prefixWithName=True,keepformat=False)
        #load openid to user info
        for groupid in self.hrd.prefix("group",2):
            self.groups[groupid[6:]]=self.hrd.getDictFromPrefix(groupid)["members"]

        for userid in self.hrd.prefix("user",2):
            key=userid[5:]
            self.users[key]=self.hrd.getDictFromPrefix(userid)
            openid=self.users[key]['openid'].strip()
            self.openidToUserId[openid]=self.users[key]

            email=self.users[key]["email"]

            if userinit:
                for groupname,members in self.groups.iteritems():
                    if email not in members:
                        #lets check if it matches one of the domain searches
                        for member in members:
                            if member.startswith("*"):
                                membersearch=member.strip("* ")
                                if email.find(membersearch)<>-1:
                                    #found user in domain
                                    self.setGroupMember(groupname,[email])
                                            
    def setUser(self,name,email,openid):
        mail2=self._mail2id(email)
        path="%s/user.%s.hrd"%(self._hrddir,mail2)
        if not j.system.fs.exists(path=path):
            j.system.fs.writeFile(filename=path,contents=userhrdtemplate)   
            self.load()
        key="user.%s"%mail2
        self.hrd.set("%s.email"%key,email)
        self.hrd.set("%s.name"%key,name)
        self.hrd.listAdd("%s.openid"%key,openid)

    def _mail2id(self,mail):
        return mail.replace("@","_").replace(".","_").lower()

    def setGroupMember(self, group,members=[]):
        group=group.strip().lower()
        path="%s/group.%s.hrd"%(self._hrddir,group)
        if not j.system.fs.exists(path=path):
            j.system.fs.writeFile(filename=path,contents=grouphrdtemplate)            
            self.load()
        
        groupobj=self.hrd.get("group.%s.members"%group)
        
        for member in members:
            if member.find("@")==-1:
                j.events.inputerror_critical("cannot add user to group, need to be specified as email","web.openid.group.mgmt.member")
            self.hrd.listAdd("group.%s.members"%group,member)

    def loggedIn(self,openid):
        return self.openidToUserId.has_key(openid)
        

usermanager=UserManagerHRD()
usermanager.setGroupMember("admin",["*@incubaid.com"])

@app.before_request
def before_request():
    g.user = None
    if 'openid' in session and usermanager.openidToUserId.has_key(session['openid']):
        g.user=usermanager.openidToUserId[session['openid']]
        print "user found"

@app.after_request
def after_request(response):    
    return response

@app.route('/')
def index():
    print "index"
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    """Does the login via OpenID.  Has to call into `oid.try_login`
    to start the OpenID machinery.
    """
    # if we are already logged in, go back to were we came from
    if g.user is not None:
        return redirect(oid.get_next_url())
    if request.method == 'POST':
        openid = request.form.get('openid')
        if openid:
            pape_req = pape.Request([])
            return oid.try_login(openid, ask_for=['email', 'nickname'],
                                         ask_for_optional=['fullname','skype'],
                                         extensions=[pape_req])
    return render_template('login.html', next=oid.get_next_url(),
                           error=oid.fetch_error())


@oid.after_login
def create_or_login(resp):
    """This is called when login with OpenID succeeded and it's not
    necessary to figure out if this is the users's first login or not.
    This function has to redirect otherwise the user will be presented
    with a terrible URL which we certainly don't want.
    """
    session['openid'] = resp.identity_url
    if 'pape' in resp.extensions:
        pape_resp = resp.extensions['pape']
        session['auth_time'] = pape_resp.auth_time

    # user = User.query.filter_by(openid=resp.identity_url).first()
    if usermanager.openidToUserId.has_key(resp.identity_url):
        flash(u'Successfully signed in')
        print "Successfully signed in"
        g.user=usermanager.openidToUserId[resp.identity_url]
        return redirect(oid.get_next_url())

    # user={}
    # for key,value in resp.__dict__.iteritems():
    #      if key<>'extensions':
    #          user[key]=value

    # json.dumps(user)

    usermanager.setUser(name=resp.fullname, email=resp.email, openid=resp.identity_url)

    from IPython import embed
    print "DEBUG NOW oooo"
    embed()
    

    if usermanager.openidToUserId.has_key(resp.identity_url):
        flash(u'Successfully signed in')
        userid=usermanager.openidToUserId[resp.identity_url]
        g.user=usermanager.users[userid]
        return redirect(oid.get_next_url())

    return redirect(oid.get_next_url())


# @app.route('/create-profile', methods=['GET', 'POST'])
# def create_profile():
#     """If this is the user's first login, the create_or_login function
#     will redirect here so that the user can set up his profile.
#     """
#     if g.user is not None or 'openid' not in session:
#         return redirect(url_for('index'))
#     if request.method == 'POST':
#         name = request.form['name']
#         email = request.form['email']
#         if not name:
#             flash(u'Error: you have to provide a name')
#         elif '@' not in email:
#             flash(u'Error: you have to enter a valid email address')
#         else:
#             flash(u'Profile successfully created')
#             db_session.add(User(name, email, session['openid']))            
#             db_session.commit()
#             return redirect(oid.get_next_url())
#     return render_template('create_profile.html', next_url=oid.get_next_url())


# @app.route('/profile', methods=['GET', 'POST'])
# def edit_profile():
#     """Updates a profile"""
#     if g.user is None:
#         abort(401)
#     form = dict(name=g.user.name, email=g.user.email)
#     if request.method == 'POST':
#         if 'delete' in request.form:
#             db_session.delete(g.user)
#             db_session.commit()
#             session['openid'] = None
#             flash(u'Profile deleted')
#             return redirect(url_for('index'))
#         form['name'] = request.form['name']
#         form['email'] = request.form['email']
#         if not form['name']:
#             flash(u'Error: you have to provide a name')
#         elif '@' not in form['email']:
#             flash(u'Error: you have to enter a valid email address')
#         else:
#             flash(u'Profile successfully created')
#             g.user.name = form['name']
#             g.user.email = form['email']
#             db_session.commit()
#             return redirect(url_for('edit_profile'))
#     return render_template('edit_profile.html', form=form)


@app.route('/logout')
def logout():
    session.pop('openid', None)
    flash(u'You have been signed out')
    return redirect(oid.get_next_url())


if __name__ == '__main__':
    app.debug=True
    app.run()
