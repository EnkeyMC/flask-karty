from flask import (Blueprint, escape, flash, render_template,
                   redirect, request, url_for,jsonify)
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import func,asc,Date,cast,extract
from sqlalchemy.types import DateTime
from .forms import ResetPasswordForm, EmailForm, LoginForm, RegistrationForm,EditUserForm,username_is_available,email_is_available,Editdate,MonthInsert
from ..data.database import db
from ..data.models import User, UserPasswordToken,Card
from ..data.util import generate_random_token
from ..decorators import reset_token_required
from ..emails import send_activation, send_password_reset
from ..extensions import login_manager
import simplejson as json
from collections import namedtuple
from datetime import datetime,timedelta

def last_day_of_month(year, month):
        """ Work out the last day of the month """
        last_days = [31, 30, 29, 28, 27]
        for i in last_days:
                try:
                        end = datetime(year, month, i)
                except ValueError:
                        continue
                else:
                        return end.day
        return None


blueprint = Blueprint('auth', __name__)

@blueprint.route('/activate', methods=['GET'])
def activate():
    " Activation link for email verification "
    userid = request.args.get('userid')
    activate_token = request.args.get('activate_token')

    user = db.session.query(User).get(int(userid)) if userid else None
    if user and user.is_verified():
        flash("Your account is already verified.", 'info')
    elif user and user.activate_token == activate_token:
        user.update(verified=True)
        flash("Thank you for verifying your email. Your account is now activated", 'info')
        return redirect(url_for('public.index'))
    else:
        flash("Invalid userid/token combination", 'warning')

    return redirect(url_for('public.index'))

@blueprint.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = EmailForm()
    if form.validate_on_submit():
        user = User.find_by_email(form.email.data)
        if user:
            reset_value = UserPasswordToken.get_or_create_token(user.id).value
            send_password_reset(user, reset_value)
            flash("Passowrd reset instructions have been sent to {}. Please check your inbox".format(user.email),
                  'info')
            return redirect(url_for("public.index"))
        else:
            flash("We couldn't find an account with that email. Please try again", 'warning')
    return render_template("auth/forgot_password.tmpl", form=form,user=current_user)

@login_manager.user_loader
def load_user(userid):  # pylint: disable=W0612
    "Register callback for loading users from session"
    return db.session.query(User).get(int(userid))

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.find_by_email(form.email.data)
        if user and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash("Logged in successfully", "info")
            return redirect(request.args.get('next') or url_for('public.index'))
        else:
            flash("Invalid email/password combination", "danger")
    return render_template("auth/login.tmpl", form=form,user=current_user)

@blueprint.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    flash("Logged out successfully", "info")
    return redirect(url_for('public.index'))

@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User.create(**form.data)
        login_user(new_user)
        send_activation(new_user)
        flash("Thanks for signing up {}. Welcome!".format(escape(new_user.username)), 'info')
        return redirect(url_for('public.index'))
    return render_template("auth/register.tmpl", form=form,user=current_user)


@blueprint.route('/resend_activation_email', methods=['GET'])
@login_required
def resend_activation_email():
    if current_user.is_verified():
        flash("This account has already been activated.", 'warning')
    else:
        current_user.update(activate_token=generate_random_token())
        send_activation(current_user)
        flash('Activation email sent! Please check your inbox', 'info')

    return redirect(url_for('public.index'))

@blueprint.route('/reset_password', methods=['GET', 'POST'])
@reset_token_required
def reset_password(userid, user_token):
    user = db.session.query(User).get(userid)
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.update(password=form.password.data)
        user_token.update(used=True)
        flash("Password updated! Please log in to your account", "info")
        return redirect(url_for('public.index'))
    return render_template("auth/reset_password.tmpl", form=form,user=current_user)
@blueprint.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    user = db.session.query(User).get(current_user.id)
    form = EditUserForm(obj = user)
    if current_user.access== "B" or current_user.access == 'U':
       form.access.choices=[('U', 'User')]
       card=form.card_number.data
    if form.validate_on_submit():
        if form.username.data <> current_user.username :
            if not username_is_available(form.username.data):
                flash("Username is not allowed use another", "warning")
                return render_template("auth/editAccountAdmin.tmpl", form=form,user=current_user)
        if form.email.data <> current_user.email:
            if not email_is_available(form.email.data):
                flash("Email is used use another email", "warning")
                return render_template("auth/editAccountAdmin.tmpl", form=form,user=current_user)
        if current_user.access <> "A":
            form.card_number.data = card
        new_user = user.update(**form.data)
        login_user(new_user)
        flash("Saved successfully", "info")
        return redirect(request.args.get('next') or url_for('public.index'))

    return render_template("auth/editAccountAdmin.tmpl", form=form,user=current_user)



@blueprint.route('/vypisy_vyber', methods=['GET','POST'])
@login_required
def mesicni_vypis_vyber():
    form = MonthInsert()
    if form.validate_on_submit():
        return redirect('/vypisy_vsichni/'+ form.month.data)
    return render_template('auth/recreatemonth.tmpl' , form = form , user = current_user)


@blueprint.route('/vypisy_vsichni/<string:mesic>', methods=['GET'])
@login_required
def vypisy_vsichni(mesic):
    #form = db.session.query( User.card_number.label('card_number'),User.full_name.label('fullname'),func.strftime('%Y-%m', Card.time).label("time"),\
    #                         func.strftime('%Y', Card.time).label("year"),func.strftime('%m', Card.time).label("month")).\
    #    join(Card,User.card_number==Card.card_number).group_by(func.strftime('%Y-%m', Card.time),User.full_name).\
    #    filter(func.strftime('%Y-%m', Card.time) == mesic).\
    #    order_by(User.full_name)
    form = db.session.query( User.card_number.label('card_number'),User.full_name.label('fullname'),func.strftime('%Y-%m', Card.time).label("time"),\
                             func.strftime('%Y', Card.time).label("year"),func.strftime('%m', Card.time).label("month"),\
                             Card.stravenky(User.card_number,func.strftime('%Y-%m', Card.time))).\
        join(Card,User.card_number==Card.card_number).group_by(func.strftime('%Y-%m', Card.time),User.full_name).\
        filter(func.strftime('%Y-%m', Card.time) == mesic).\
        order_by(User.full_name).all()

    return render_template("auth/vypisy_vsichni.tmpl", form=form,user=current_user)


@blueprint.route('/vypisy', methods=['GET'])
@login_required
def vypisy():

    #form=Card.find_by_number(current_user.card_number)
    #form = db.session.query(Card.time).filter_by(card_number=current_user.card_number)
    form = db.session.query( func.strftime('%Y-%m', Card.time).label("time"),func.strftime('%Y', Card.time).label("year"),func.strftime('%m', Card.time).label("month")).filter_by(card_number=current_user.card_number).group_by(func.strftime('%Y-%m', Card.time))
        #.group_by([func.day(Card.time)])

    return render_template("auth/vypisy.tmpl", form=form, data=current_user.card_number,user=current_user)

@blueprint.route('/mesicni_vypis_vsichni/<string:mesic>', methods=['GET'])
@login_required
def mesicni_vypis_alluser(mesic):

    #form=Card.find_by_number(current_user.card_number)
    #form = db.session.query(Card.time).filter_by(card_number=current_user.card_number)
    form = db.session.query( func.strftime('%Y-%m-%d', Card.time).label("date"),func.max(func.strftime('%H:%M', Card.time)).label("Max"),\
                             func.min(func.strftime('%H:%M', Card.time)).label("Min"),( func.max(Card.time) - func.min(Card.time)).label("Rozdil"))\
        .filter(func.strftime('%Y-%-m', Card.time) == mesic).group_by(func.strftime('%Y-%m-%d', Card.time))
        #.group_by([func.day(Card.time)])
    return render_template("auth/mesicni_vypisy.tmpl", form=form,user=current_user)


@blueprint.route('/mesicni_vypis/<string:mesic>', methods=['GET'])
@login_required
def mesicni_vypis(mesic):

    #form=Card.find_by_number(current_user.card_number)
    #form = db.session.query(Card.time).filter_by(card_number=current_user.card_number)
    form = db.session.query( func.strftime('%Y-%m-%d', Card.time).label("date"),func.max(func.strftime('%H:%M', Card.time)).label("Max"),\
                             func.min(func.strftime('%H:%M', Card.time)).label("Min"),( func.max(Card.time) - func.min(Card.time)).label("Rozdil"))\
        .filter((func.strftime('%Y-%-m', Card.time) == mesic) and (Card.card_number == current_user.card_number)).group_by(func.strftime('%Y-%m-%d', Card.time))
        #.group_by([func.day(Card.time)])
    return render_template("auth/mesicni_vypisy.tmpl", form=form,user=current_user)


from collections import OrderedDict
class DictSerializable(object):
    def _asdict(self):
        result = OrderedDict()
        for key in self.__mapper__.c.keys():
            result[key] = getattr(self, key)
        return result

@blueprint.route('/tbl_isdata/<int:od>/<int:do>', methods=['GET'])
@login_required
def tbl_insdata(od , do ):
    #data = db.session.query( func.strftime('%Y-%m', Card.time).label("time")).filter_by(card_number=current_user.card_number).group_by(func.strftime('%Y-%m', Card.time))
    if od==0 and do == 0 :
        data=db.session.query(Card.id,Card.card_number,func.strftime('%Y-%m', Card.time).label("time")).all()
    else:
        data=db.session.query(Card.id,Card.card_number,func.strftime('%Y-%m', Card.time).label("time")).slice(od,do)
    pole=['id','time','card_number']
    result = [{col: getattr(d, col) for col in pole} for d in data]
    return jsonify(data = result)




@blueprint.route('/tabletest', methods=['GET'])
@login_required
def tabletest():
    return render_template('public/table.tmpl',user=current_user)

@blueprint.route('/caljsonr/<int:card_number>/<int:year>/<int:mount>', methods=['GET'])
@login_required
def caljson_edit(card_number,year,mount):
    lastday = last_day_of_month(year , mount)
    data=[]
    startdate='8:00'
    enddate='16:00'
    for day in xrange(1,lastday):
        d = {}
        d['card_number']=card_number
        d['day']=day
        d['startdate']=startdate
        d['enddate']=enddate
        data.append(d)
    #print json.dumps(data, separators=(',',':'))

    #pole=['card_number','day','startdate','enddate']
    #result = [{col: d[col] for col in pole} for d in data]
    #print jsonify(data=result)



    #return render_template('auth/calendar.tmpl')
    return jsonify(data=data)

@blueprint.route('/calendar/<int:card_number>/<int:year>/<int:mounth>', methods=['GET'])
@login_required
def calendar(card_number,year,mounth):
    lastday = last_day_of_month(year , mounth)

    datarow=[]
    data={}
    startdate='0:00'
    enddate='0:00'
    data['stravenka']=0
    #hodnota = list(db.session.query( func.strftime('%d', Card.time).label("den"),func.max(func.strftime('%H:%M', Card.time)).label("Max"),\
    #                         func.min(func.strftime('%H:%M', Card.time)).label("Min"))\
    #                        .filter(func.date(Card.time) == fromdate.date()).filter(Card.card_number == card_number).group_by(func.date(Card.time)))
    ff= datetime(year, mounth, 1).strftime('%Y-%-m')
    #hodnota = list(db.session.query( func.strftime('%d', Card.time).label("den"),func.max(func.strftime('%H:%M', Card.time)).label("Max"),\
     #                        func.min(func.strftime('%H:%M', Card.time)).label("Min"))\
      #                   .filter(Card.card_number == card_number).group_by(func.strftime('%Y-%m-%d', Card.time)))


    hodnota = list(db.session.query( extract('day', Card.time).label("den")\
                        ,func.min(func.strftime('%H:%M', Card.time)).label("Min")\
                        ,func.max(func.strftime('%H:%M', Card.time)).label("Max"))\
                        .filter(extract('month', Card.time) == mounth  ) .filter(extract('year', Card.time) == year  ).filter(Card.card_number==card_number).group_by(func.strftime('%Y-%m-%d', Card.time)))
            #.filter(datetime(Card.time).month == mounth  ))
    for day in xrange(1,lastday):
        d = {}
        d['day']=day
        d['dow']= datetime(year, mounth, day).weekday()
        datafromdb=filter(lambda x: x[0] == day, hodnota)
        if d['dow'] > 4:
            d['startdate']=''
            d['enddate']=''
        else:
            fromdate=datetime(year, mounth, day)
            todate=datetime(year, mounth, day) + timedelta(days=1)

            #hodnota = db.session.query( func.min(func.strftime('%H:%M', Card.time)).label("Min")).filter(Card.time >= fromdate).filter(Card.time < todate).filter(Card.card_number == card_number)
            #hodnota = list(db.session.query(func.date(Card.time).label('xxx')).filter(func.date(Card.time) == fromdate.date() ).filter(Card.card_number == card_number).all())
            #.filter(cast(Card.time,Date) == fromdate.date())
            #hodnota = list(db.session.query( func.strftime('%d', Card.time).label("den"),func.max(func.strftime('%H:%M', Card.time)).label("Max"),\
             #                func.min(func.strftime('%H:%M', Card.time)).label("Min"))\
             #               .filter(func.date(Card.time) == fromdate.date()).filter(Card.card_number == card_number).group_by(func.date(Card.time)))
                           #.group_by(func.strftime('%Y-%m-%d', Card.time)))
#            if len(hodnota) > 0 :
 #               print len(hodnota)

            d['startdate']=startdate
            d['enddate']=enddate
            if datafromdb :
                d['startdate']=datafromdb[0][1]
                d['enddate']=datafromdb[0][2]
            rozdil=datetime.strptime(d['enddate'],"%H:%M")-datetime.strptime(d['startdate'],"%H:%M")
            d['timespend']=round(rozdil.total_seconds() / 3600,2)
            if d['timespend'] >= 3:
                data['stravenka'] = data['stravenka'] + 1

        datarow.append(d)
    data['user']=current_user.email
    data['mounth']=mounth
    data['year']=year
    data['card_number']=card_number
    data['data']=datarow


    return render_template('auth/mesicni_vypis.tmpl',data=data,user=current_user)

@blueprint.route('/calendar_edit/<int:card_number>/<int:year>/<int:mounth>/<int:day>', methods=['GET','POST'])
@login_required
def calendar_edit(card_number,year,mounth,day):
    form = Editdate()
    form.den = str(day)  + '-' +  str(mounth)  +  '-' + str(year)
    form.card_number = str (card_number)
    if form.validate_on_submit():
        delday=db.session.query(Card).filter(extract('month', Card.time) == mounth  ) .filter(extract('year', Card.time) == year  ).filter(extract('day', Card.time) == day  ).filter(Card.card_number==card_number)
        for item in delday:
            db.session.delete(item)
        time1=str(day)  + '-' +  str(mounth)  +  '-' + str(year)+' '+ str(form.data['startdate'])
        cas= datetime.strptime(time1, "%d-%m-%Y %H:%M:%S")
        i=Card(card_number=card_number,time=cas)
        db.session.add(i)
        time1=str(day)  + '-' +  str(mounth)  +  '-' + str(year)+' '+ str(form.data['enddate'])
        cas= datetime.strptime(time1, "%d-%m-%Y %H:%M:%S")
        i=Card(card_number=card_number,time=cas)
        db.session.add(i)
        db.session.commit()
        flash("Saved successfully", "info")
        return redirect('calendar/'+str (card_number)+'/'+str(year)+'/'+str(mounth))
    return render_template('auth/editdate.tmpl', form=form,user=current_user)

@blueprint.route('/user_list', methods=['GET'])
@login_required
def user_list():
    if current_user.access== "A" or current_user.access== "B":
        data = list(db.session.query(User).all())
        return render_template('auth/user_list.tmpl',data=data,user=current_user)
    else:
        flash("Access deny", "warn")
        return redirect('/')

@blueprint.route('/user_edit/<int:id>', methods=['GET','POST'])
@login_required
def user_edit(id):
    #if current_user.email== "admin@iservery.com":
    user = db.session.query(User).get(id)
    if current_user.access <> 'A'and user.access=='A':
        flash("Edit not allowed", "info")
        return redirect(request.args.get('next') or url_for('auth.user_list'))
    form = EditUserForm(obj = user)
    if current_user.access== "B":
       form.access.choices=[('U', 'User')]
    if form.validate_on_submit():
        new_user = user.update(**form.data)
        flash("Saved successfully", "info")
        return redirect(request.args.get('next') or url_for('auth.user_list'))
    return render_template("auth/editAccountAdmin.tmpl", form=form,user=current_user)

@blueprint.route('/user_del/<int:id>', methods=['GET','POST'])
@login_required
def user_del(id):
    user=db.session.query(User).filter_by(id = id).first()
    if current_user.access <> 'A'and user.access=='A':
        flash("remove not allowed", "info")
        return redirect(request.args.get('next') or url_for('auth.user_list'))
    db.session.delete(user)
    db.session.commit()
    flash("User Removed", "info")
    return redirect(request.args.get('next') or url_for('auth.user_list'))



@blueprint.route('/user_add/', methods=['GET','POST'])
@login_required
def user_add():
    if current_user.access== "A" or current_user.access== "B":
        form = EditUserForm()
        if current_user.access== "B":
            form.access.choices=[('U', 'User')]
        if form.validate_on_submit():
            if not username_is_available(form.username.data):
                    flash("Username is not allowed use another", "warning")
                    return render_template("auth/editAccountAdmin.tmpl", form=form,user=current_user)
            if not email_is_available(form.email.data):
                    flash("Email is used use another email", "warning")
                    return render_template("auth/editAccountAdmin.tmpl", form=form,user=current_user)

            new_user = User.create(**form.data)
            flash("Saved successfully", "info")
            return redirect(request.args.get('next') or url_for('auth.user_list'))

        return render_template("auth/editAccountAdmin.tmpl", form=form,user=current_user)
    else:
            flash("Access Deny", "warn")
            return redirect(request.args.get('next') or url_for('public.index'))

@blueprint.route('/newmonth', methods=['GET','POST'])
@login_required
def newmonth():
    form = MonthInsert()
    if form.validate_on_submit():
        return redirect('/recreatemonth/'+ form.month.data)
    return render_template('auth/recreatemonth.tmpl' , form = form , user = current_user)

@blueprint.route('/recreatemonth/<string:month>', methods=['GET'])
@login_required
def createmonth(month):
    datum=datetime.strptime(month + '-1',"%Y-%m-%d")
    users=db.session.query(User).filter(Card.card_number <> '').all()
    for user in users:
        if not list(db.session.query(Card).filter(Card.card_number == user.card_number).filter(func.strftime('%H:%M', Card.time) == month)):
            i=Card(card_number=user.card_number,time=datum)
            db.session.add(i)
    db.session.commit()
    flash("Mesic vytvoren", "info")
    return redirect(request.args.get('next') or url_for('public.index'))

