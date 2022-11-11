from flas import Flask, render_template,flash,redirect,request, session, send_from_directory, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
from flask_bootstrap import Bootstrap
from datetime import datetime

app=Flask(__name__)
Bootstrap(app)
app.secret_key="123"
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY']='asfas'
app.config['UPLOADED_PHOTOS_DEST']='uploads'

photos=UploadSet('photos', IMAGES)
configure_uploads(app, photos)

class UploadForm(FlaskForm):
    photo=FileField(
        validators=[
            FileAllowed(photos, "only images are allowed"),
            FileRequired('file field should not be empty ')
        ]
    )
    submit=SubmitField('Upload')

@app.route('/<filename>')
def get_file(filename):

    return send_from_directory(app.config['UPLOADED_PHOTOS_DEST'], filename)



@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form=UploadForm()
    if form.validate_on_submit():
        filename=photos.save(form.photo.data)
      
        file_url=url_for('get_file', filename=filename)
    else:
        file_url=None
    return render_template('upload.html', form=form, file_url=file_url)



db = SQLAlchemy(app)


class Users(db.Model):
    __tablename__='users'
    user_id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(100), nullable=False)
    mail=db.Column(db.String(100), nullable=False)
    password=db.Column(db.String(100), nullable=False)
    phone=db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    user_cars = relationship("Cars", back_populates = "owner", cascade="all, delete-orphan")


    def __repr__(self):
        return f'<Users {self.user_id}>' 


class Message(db.Model):
    __tablename__='message'
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(100), nullable=False)
    email=db.Column(db.String(100), nullable=False)
    subject=db.Column(db.String(100), nullable=False)
    Message=db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Message {self.id}>' 

class Cars(db.Model):
    __tablename__='cars'
    car_id=db.Column(db.Integer, primary_key=True)
    year=db.Column(db.Integer)
    mileage=db.Column(db.Integer)
    price=db.Column(db.Integer)
    car_model=db.Column(db.String(100), nullable=False)
    description=db.Column(db.Text)
   
    car_owner=db.Column(db.Integer, db.ForeignKey('users.user_id'))


    owner = relationship("Users", back_populates="user_cars")

    def __repr__(self):
        return f'<Cars {self.car_id}>' 

        


@app.route("/user/<int:user_id>")
def user_page(user_id, context=None):
    query = db.session.query(Users).join(Cars).filter(Cars.car_owner == user_id).all()
    if query:
        return render_template("user_page.html", context=query)
    else:
        query = db.session.query(Users).filter(Users.user_id == user_id).first()
        return render_template("user_page.html", context=query)


@app.route("/login", methods = ["GET", "POST"])
def login(context=None):
    message={}
    if request.method == "POST":
        user = db.session.query(Users).filter_by(mail=request.form['mail'], password=request.form['password']).first()
        print(user)
        if user:
            session['authenticated'] = True
            session['uid'] = user.user_id
            session['username'] = user.username
            session["mail"]=user.mail
            session['phone']=user.phone
            return redirect(url_for('user_page', user_id=user.user_id))
        else:
            flash('Incorrect data, try again.', category='error')
    
    return render_template("login.html", context=context)


@app.route("/logout")
def logout():
    session.pop('authenticated', None)
    session.pop('uid', None)
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/register', methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        mail = request.form['mail']
        password = request.form['password']
        phone=request.form['phone']

        data = db.session.query(Users).filter_by(username=request.form['username']).first()
        
        if data:
            flash('Already exists account', category='error')
           
            return redirect(url_for('register'))
        else:
            new_user=(Users(username=username,
                        mail=mail,
                        password=password,
                        phone=phone))
            db.session.add(new_user)
            db.session.commit()
            flash('Account created!', category='success')
            return redirect(url_for("register", context="Succesfully registered!"))
    return render_template('register.html')


@app.route("/update", methods = ["GET", "POST"])
def update():
    if request.method=="POST":
        if "username" in session and "mail" in session:
            session['username']=request.form['username']
            session['mail']=request.form['mail']
            
            db.session.query(Users).filter_by(username=session['username'], mail=session['mail']).first()
            new_user=(Users(username=session['username'],
                            mail=session['mail']))
            try:
                db.session.add(new_user)
                db.session.commit()

                flash("Record updated successfully!",category='success')
                return redirect(url_for('my_profile'), user_id=session['uid'])
            except:
                flash("Record not updated successfully!",category='error')
                return redirect(url_for('index'))
        else:
            flash('wrong', category='error')
            return redirect(url_for('index'))

    return render_template("update.html")



@app.route("/delete")
def delete():
    if "username" in session and "mail" in session:
        username = session["username"]
        mail = session["mail"]
        Users.query.filter_by(username=username).delete()
        Users.query.filter_by(mail=mail).delete()
        db.session.commit()
        flash("Record deleted successfully!",category='success')
        session.pop('authenticated', None)
        session.pop('uid', None)
        session.pop('username', None)
    elif "username" in session and "mail" not in session:
        username = session["username"]
        if not Users.query.filter_by(username=username).first():
            flash("Unable to delete since there is no record found!")
        else:
            Users.query.filter_by(username=username).delete()
            db.session.commit()
            flash("Record deleted successfully!", category='success')
            session.pop('authenticated', None)
            session.pop('uid', None)
            session.pop('username', None)
    else:
        flash("Unable to delete record!", category='error')
    return redirect(url_for("index"))




    
    
@app.route('/')
def index():
   return render_template('index.html')


@app.route('/about')
def about():
   return render_template('about.html')



@app.route('/team')
def team():
   return render_template('team.html')


@app.route('/contact',  methods = ["GET", "POST"])
def contact():
    if request.method=="POST":
        name = request.form['fname']
        email = request.form['femail']
        subject = request.form['fsubject']
        message=request.form['fphone']
        new_message=(Message(name=name,
                        email=email,
                        subject=subject,
                        message=message))
        db.session.add(new_message)
        db.session.commit()
        flash('Account created!', category='success')
        return redirect(url_for("index", context="Succesfully registered!"))

    return render_template('contact.html')
   


#@app.route('/cars')
#def cars():
#    user_id=session['uid']
#    query = db.session.query(Users).join(Cars).all()
#    if query:
#        return render_template("cars.html", context=query)
#    else:
#        query = db.session.query(Users).all()
#        return render_template("cars.html", context=query)

@app.route('/my_profile/<int:user_id>')
def my_profile(user_id, context=None):
    return render_template('my_profile.html', user_id=user_id)


@app.route('/my_cars/<int:user_id>', methods = ["GET", "POST"])
def my_cars(user_id, context=None):
    query = db.session.query(Users).join(Cars).filter(Cars.car_owner == user_id).all()
    if query:
        return render_template("my_cars.html", context=query)
    else:
        query = db.session.query(Users).filter(Users.user_id == user_id).first()
        return render_template("my_cars.html", context=query)


@app.route('/cars')
def cars():
    cars=Cars.query.all()
    return render_template('cars.html', cars=cars)
    
    
@app.route('/add_car/<int:user_id>' , methods = ["GET", "POST"])
def add_car(user_id, context=None):
    if request.method == "POST":
        car_model = request.form['car_model']
        year = request.form['year']
        mileage = request.form['mileage']
        price = request.form['price']
        description = request.form['description']
        
        new_car=(Cars(car_model=car_model,
                        year=year,
                        mileage=mileage,
                        price=price,
                        description=description,
                        car_owner=session['uid']
                        ))
        try:
            db.session.add(new_car)
            db.session.commit()
            
            flash('car successfully added!', category='success')
            return redirect(url_for('index'))
        except:
            flash('the is some problem!', category='error')
            return redirect(url_for('index'))
    return render_template('add_car.html', user_id=user_id)





if __name__=='__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True, port=5000)
