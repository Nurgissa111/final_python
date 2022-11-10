from flask import Flask, render_template,request, session
from flask_sqlalchemy import SQLAlchemy

from flask_uploads import IMAGES, UploadSet, configure_uploads, patch_request_class
import os



basedir=os.path.abspath(os.path.dirname(__file__))

app=Flask(__name__)

app.secret_key="123"
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['UPLOADED_PHOTOS_DEST']=os.path.join(basedir, 'static/images')
app.config["MAX_CONTENT_LENGTH"] = 120 * 1024 * 1024

photos=UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)

db = SQLAlchemy(app)


class Car(db.Model):
    mail=db.Column(db.String(100), nullable=False)
    phone=db.Column(db.Integer,nullable=False)
    password=db.Column(db.String(100), nullable=False)
    image=db.Column(db.String(150), nullable=False, default='image.jpg')

class Users(db.Model):
    user_id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(100), nullable=False)


    #user_portfolies = relationship("Portfolio", back_populates = "owner", cascade="all, delete-orphan")


    def __repr__(self):
        return f'<Users {self.user_id}>' 


 


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/images', methods=['GET','POST'])
def images():
    users=Users.query.all()
    form=Car(request.form)
    if request.method=='POST':
        photos.save(request.files.get('image'))
    return render_template('index.html', form=form, users=users)

if __name__=='__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True, port=5000)

if request.method=="POST":
        if "username" in session and "mail" in session:
            username = session["username"]
            mail = session["mail"]
            username=request.form['username']
            mail=request.form['mail']
            
            new_user=(Users(username=username,
                            mail=mail))
            try:
                db.session.add(new_user)
                db.session.commit()
                flash("Record updated successfully!",category='success')
                return redirect(url_for("my_profile", user_id=session['uid']))

            except:
                flash("There is a problem!",category='error')
        else:
            flash("Unable to update record!", category='error')
    else: