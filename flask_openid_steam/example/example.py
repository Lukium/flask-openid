#!/bin/env python
# -*- coding: utf-8 -*-
"""
    OpenID Example
    ~~~~~~~~~~~~~~

    This simple application shows how to integrate OpenID in your application.

    This example requires SQLAlchemy as a dependency.

    :copyright: (c) 2010 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""
from flask import (
    Flask,
    render_template,
    request,
    g,
    session,
    flash,
    redirect,
    url_for,
    abort,
)
from flask_openid_steam.flask_openid_steam import OpenID

from openid.extensions import pape

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# setup flask
app = Flask(__name__)
app.config.update(
    DATABASE_URI="sqlite:///flask-openid.db",
    SECRET_KEY="development key",
    DEBUG=True,
)

# setup flask-openid
oid = OpenID(app, safe_roots=[], extension_responses=[pape.Response])

# setup sqlalchemy
engine = create_engine(app.config["DATABASE_URI"])
db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=True, bind=engine)
)
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    Base.metadata.create_all(bind=engine)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(60))
    email = Column(String(200))
    openid = Column(String(200))

    def __init__(self, name, email, openid):
        self.name = name
        self.email = email
        self.openid = openid


@app.before_request
def before_request():
    g.user = None
    if "openid" in session:
        g.user = User.query.filter_by(openid=session["openid"]).first()


@app.after_request
def after_request(response):
    db_session.remove()
    return response


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
@oid.loginhandler
def login():
    """Does the login via OpenID.  Has to call into `oid.try_login`
    to start the OpenID machinery.
    """
    # if we are already logged in, go back to were we came from
    if g.user is not None:
        return redirect(oid.get_next_url())
    if request.method == "POST":
        openid = request.form.get("openid")
        if openid:
            pape_req = pape.Request([])
            return oid.try_login(
                openid,
                ask_for=["email", "nickname"],
                ask_for_optional=["fullname"],
                extensions=[pape_req],
            )
    return render_template(
        "login.html", next=oid.get_next_url(), error=oid.fetch_error()
    )


@oid.after_login
def create_or_login(resp):
    """This is called when login with OpenID succeeded and it's not
    necessary to figure out if this is the users's first login or not.
    This function has to redirect otherwise the user will be presented
    with a terrible URL which we certainly don't want.
    """
    session["openid"] = resp.identity_url
    if "pape" in resp.extensions:
        pape_resp = resp.extensions["pape"]
        session["auth_time"] = pape_resp.auth_time
    user = User.query.filter_by(openid=resp.identity_url).first()
    if user is not None:
        flash("Successfully signed in")
        g.user = user
        return redirect(oid.get_next_url())
    return redirect(
        url_for(
            "create_profile",
            next=oid.get_next_url(),
            name=resp.fullname or resp.nickname,
            email=resp.email,
        )
    )


@app.route("/create-profile", methods=["GET", "POST"])
def create_profile():
    """If this is the user's first login, the create_or_login function
    will redirect here so that the user can set up his profile.
    """
    if g.user is not None or "openid" not in session:
        return redirect(url_for("index"))
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        if not name:
            flash("Error: you have to provide a name")
        elif "@" not in email:
            flash("Error: you have to enter a valid email address")
        else:
            flash("Profile successfully created")
            db_session.add(User(name, email, session["openid"]))
            db_session.commit()
            return redirect(oid.get_next_url())
    return render_template("create_profile.html", next_url=oid.get_next_url())


@app.route("/profile", methods=["GET", "POST"])
def edit_profile():
    """Updates a profile"""
    if g.user is None:
        abort(401)
    form = dict(name=g.user.name, email=g.user.email)
    if request.method == "POST":
        if "delete" in request.form:
            db_session.delete(g.user)
            db_session.commit()
            session["openid"] = None
            flash("Profile deleted")
            return redirect(url_for("index"))
        form["name"] = request.form["name"]
        form["email"] = request.form["email"]
        if not form["name"]:
            flash("Error: you have to provide a name")
        elif "@" not in form["email"]:
            flash("Error: you have to enter a valid email address")
        else:
            flash("Profile successfully created")
            g.user.name = form["name"]
            g.user.email = form["email"]
            db_session.commit()
            return redirect(url_for("edit_profile"))
    return render_template("edit_profile.html", form=form)


@app.route("/logout")
def logout():
    session.pop("openid", None)
    flash("You have been signed out")
    return redirect(oid.get_next_url())


if __name__ == "__main__":
    init_db()
    app.run()
