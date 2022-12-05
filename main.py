from flask import render_template, request, redirect, url_for, flash, g
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from models import User, Url, obj_add, obj_delete
from app import app, db
from utils import get_short_urls, get_obj_url, generate_key
from validators import validate_url, check_base_url


@app.route("/<name>", methods=["POST", "GET"])
def main_page(name="hello"):
    if current_user.is_authenticated:
        context = dict()
        if request.method == "POST" and not check_base_url(user=current_user, base_url=request.form.get("url")):
            if validate_url(request.form.get("url")):
                data = dict(
                    key=generate_key(),
                    base_url=request.form.get("url"),
                    user_id=current_user.id
                )
                obj_add(Url(**data))
                context["urls"] = get_short_urls(current_user, request.host)
            else:
                flash("Don't validate url")
        else:
            if name == current_user.name:
                context["urls"] = get_short_urls(current_user, request.host)
            else:
                obj_url = get_obj_url(name)
                if obj_url:
                    obj_url.clicks += 1
                    db.session.commit()
                    return redirect(obj_url.base_url)
                else:
                    flash("This page not found")
                    if current_user.is_authenticated:
                        return redirect(url_for('main_page', name=current_user.name))
                    return render_template('login.html', title="Authorization"), 404
    else:
        obj_url = get_obj_url(name)
        if obj_url:
            obj_url.clicks += 1
            db.session.commit()
            return redirect(obj_url.base_url)
        else:
            flash("This page not found")
            return render_template('login.html', title="Authorization"), 404
    return render_template("main.html", title="Shortcuster", name=name, **context)


@app.route('/login', methods=["POST", "GET"])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('main_page', name=current_user.name))
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        if email and password:
            user = User.query.filter_by(email=email).first()
            if user and check_password_hash(user.password, password):
                login_user(user)
                next_page = request.args.get('next')
                flash(f"Hello, {user.name.capitalize()}")
                return redirect(next_page or url_for("main_page", name=current_user.name))
            else:
                flash('Login or password is not correct')
        else:
            flash('Please fill login and password fields')
    return render_template('login.html', title="Authorization")


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        data = dict(request.form)
        if not (data.get("email") or data.get("password") or data.get("password2") or data.get("name")):
            flash('Please, fill all fields!')
        elif data.get("password") != data.get("password2"):
            flash('Passwords are not equal!')
        else:
            del data["password2"]
            data["password"] = generate_password_hash(data.get("password"))
            obj_add(User(**data))
            return redirect(url_for('login_page'))

    return render_template('register.html', title="Register")


@app.route("/delete-link", methods=["POST", "GET"])
@login_required
def delete_link_page():
    data = request.form
    if data.get("link"):
        if obj_url := get_obj_url(data.get("link")):
            obj_delete(obj_url)
            flash(f"This link {obj_url.base_url} was deleted")
            return redirect(url_for('main_page', name=current_user.name))
    return redirect(url_for('main_page', name=current_user.name))


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout_page():
    logout_user()
    return redirect(url_for('login_page'))


@app.teardown_appcontext
def close(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.errorhandler(401)
def error_page(error):
    flash(error)
    return redirect(url_for('login_page')), 401


@app.errorhandler(403)
def error_page1(error):
    flash(error)
    return render_template('login.html', title="Authorization"), 403


@app.errorhandler(404)
def error_page1(error):
    flash(error)
    return render_template('login.html', title="Authorization"), 404


@app.errorhandler(500)
def error_page1(error):
    flash(error)
    return render_template('login.html', title="Authorization"), 500


if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
