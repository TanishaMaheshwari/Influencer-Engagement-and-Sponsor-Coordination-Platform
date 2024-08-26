from flask import render_template, request, flash, redirect, url_for, session
from app import app
from models import db, User, Sponsor, Influencer, Admin, Campaign, Adrequest, Application, Payment, Request
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime


# ____________________Authorization Decorators_________________ 

def auth_req(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'user_id' in session:
            return func(*args, **kwargs)
        else:
            flash('Please Login to continue.')
            return redirect(url_for('login'))   
    return inner

def sponsor_req(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please Login to continue.')
            return redirect(url_for('login'))  
        user = User.query.get(session['user_id']) 
        if user.Role != 'Sponsor':
            flash('You are not authorized to access this page.')
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    return inner

def admin_req(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please Login to continue.')
            return redirect(url_for('login'))  
        user = User.query.get(session['user_id']) 
        if user.Role != 'Admin':
            flash('You are not authorized to access this page.')
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    return inner

def influencer_req(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please Login to continue.')
            return redirect(url_for('login'))  
        user = User.query.get(session['user_id']) 
        if user.Role != 'Influencer':
            flash('You are not authorized to access this page.')
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    return inner



# _______________________BASIC ROUTES_______________________

@app.route('/')
def index():
    return render_template('index.html') 

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        flash('Fill out all the required details.')
        return redirect(url_for('login'))
    
    user = User.query.filter_by(username=username).first()

    if not user:
        flash('Username does not exists.')
        return redirect(url_for('login'))
    
    if not check_password_hash(user.passhash, password):
        flash('Incorrect Password.')
        return redirect(url_for('login'))

    session['user_id'] = user.id 
    session['user_role'] = user.Role
    
    if user.Role == 'Sponsor':
        sponsor = Sponsor.query.filter_by(username=user.username).first()
        return redirect(url_for('sponsor',  sponsor_id = sponsor.id))
    
    elif user.Role == 'Influencer':
        influencer = Influencer.query.filter_by(username=user.username).first()
        return redirect(url_for('influencer',  influencer_id = influencer.id))

    else:
        return redirect(url_for('admin'))
    
    return redirect(url_for('index'))

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_post():
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    role = request.form.get('gridRadios')

    if not username or not password or not confirm_password or not role:
        flash('Fill out all the required details.')
        return redirect(url_for('register'))
    
    if username == password:
        flash('Username can not be your password.')
        return redirect(url_for('register'))
    
    if password != confirm_password:
        flash('Passwords do not match.')
        return redirect(url_for('register'))
    
    user = User.query.filter_by(username=username).first()

    if user:
        flash('Username already exists.')
        return redirect(url_for('register'))
    
    password_hash = generate_password_hash(password)

    new_user = User( username=username, passhash=password_hash, Role=role)
    db.session.add(new_user)
    db.session.commit()

    if role == 'Sponsor':
           sponsor = Sponsor(username=username, CompanyName='', Industry='', Budget=0, Flag=False)
           db.session.add(sponsor)
           db.session.commit()
    elif role == 'Admin':
           admin = Admin(username=username)
           db.session.add(admin)
           db.session.commit()
    elif role == 'Influencer':
           influencer = Influencer(username=username, Niche='', Category='', Reach=0, Flag=False)
           db.session.add(influencer)
           db.session.commit()

    return redirect(url_for('login'))

@app.route('/profile')
@auth_req
def profile():
    user = User.query.get(session['user_id'])

    if user.Role == 'Sponsor':
        sponsor = Sponsor.query.filter_by(username=user.username).first()
        return render_template('sponsor/profile.html', sponsor=sponsor)
    
    elif user.Role == 'Influencer':
        influencer = Influencer.query.filter_by(username=user.username).first()
        return render_template('influencer/profile.html', influencer=influencer)

    else:
        return redirect(url_for('admin'))
    
    return render_template('profile.html', user = user)

@app.route('/passchange')
@auth_req
def passchange():
    user =  User.query.get(session['user_id'])
    return render_template('pass.html', user=user)

@app.route('/passchange', methods = ['POST'])
@auth_req
def passchange_post():
    username = request.form.get('username')
    cpassword = request.form.get('cpassword')
    password = request.form.get('password')

    if not username or not cpassword or not password:
        flash ('Fill out all the details.')
        return redirect(url_for('profile'))
    
    user=User.query.get(session['user_id'])
    if not check_password_hash(user.passhash, cpassword):
        flash('Incorrect Password.')
        return redirect(url_for('profile'))
    
    if username != user.username:
        new_user = User.query.filter_by(username=username).first()
        if new_user:
            flash('Username already exists.')
            return redirect(url_for('profile'))
        
    new_password_hash = generate_password_hash(password)
    user.username = username
    user.passhash = new_password_hash
    db.session.commit()
    flash('Password changed succesfully.')
    return redirect(url_for('profile'))

@app.route('/logout')
@auth_req
def logout():
    session.pop('user_id')
    return redirect(url_for('index'))

@app.route('/transcript/<int:id>')
@auth_req
def transcript(id):
    payment = Payment.query.get(id)
    inf_id = payment.InfluencerId
    influencer = Influencer.query.get(inf_id)
    spn_id = payment.SponsorId
    sponsor = Sponsor.query.get(spn_id)
    return render_template('Transcript.html', payment = payment, influencer=influencer, sponsor=sponsor)

# _______________________SPONSOR PAGES________________________

@app.route('/sponsor/<int:sponsor_id>')
@sponsor_req
def sponsor(sponsor_id): 
    sponsor = Sponsor.query.get(sponsor_id)

    if not sponsor:
        flash('sponsor does not exist.')
        return redirect(url_for('login'))
    
    if sponsor.Flag==True:
        flash('You are flagged by the Admin.')
        return redirect(url_for('login'))

    influencer = Influencer.query.filter(~Influencer.id.in_(db.session.query(Request.InfluencerId).filter(Request.SponsorId == sponsor_id))).all()
    
    niche = request.args.get('niche') or ''
    cat_name = request.args.get('cat_name') or ''
    reach = request.args.get('reach')
    
    if reach:
            try:
                reach = int(reach)
            except ValueError:
                flash('Invalid reach')
                return redirect(url_for('sponsor', sponsor_id=session['user_id']))
            if reach <= 0:
                flash('Invalid reach')
                return redirect(url_for('sponsor', sponsor_id=session['user_id']))

    if niche:
        influencer = Influencer.query.filter(Influencer.Niche.ilike(f'%{niche}%')).all()

    if cat_name:
        influencer = Influencer.query.filter(Influencer.Category.ilike(f'%{cat_name}%')).all()

    applications = [app for app in sponsor.Applications02 if app.Approval == False]
    return render_template('sponsor/home.html', campaigns = sponsor.Campaigns, applications = applications, influencers=influencer, niche=niche, cat_name=cat_name, reach=reach )

@app.route('/sponsor')
def sponsor_home():
    user =  User.query.get(session['user_id'])
    sponsor = Sponsor.query.filter_by(username=user.username).first()
    return redirect(url_for('sponsor', sponsor_id=sponsor.id))

@app.route('/sponsor/<int:sponsor_id>/delete')
@sponsor_req
def sponsor_delete(sponsor_id): 
    sponsor = Sponsor.query.get(sponsor_id)
    if not sponsor:
        flash('sponsor doen not exist.')
        return redirect(url_for('login'))

    return render_template('sponsor/delete.html', sponsor=sponsor)

@app.route('/sponsor/<int:sponsor_id>/delete', methods=['POST'])
@sponsor_req
def sponsor_delete_post(sponsor_id): 
    sponsor = Sponsor.query.get(sponsor_id)
    user = User.query.filter_by(username=sponsor.username).first()
    if not sponsor:
        flash('sponsor doen not exist.')
        return redirect(url_for('login'))
    db.session.delete(sponsor)
    db.session.delete(user)
    db.session.commit()

    flash('Account deleted successfully.')
    return redirect(url_for('login'))

@app.route('/sponsor/<int:sponsor_id>/update')
@sponsor_req
def sponsor_update(sponsor_id):
    sponsor = Sponsor.query.get(sponsor_id)
    if not sponsor:
        flash('sponsor does not exist.')
        return redirect(url_for('login'))
    return render_template('sponsor/update.html', sponsor=sponsor)

@app.route('/sponsor/<int:sponsor_id>/update', methods=['POST'])
@sponsor_req
def sponsor_update_post(sponsor_id):
    sponsor = Sponsor.query.get(sponsor_id)
    if not sponsor:
        flash('sponsor does not exist.')
        return redirect(url_for('login'))
        
    name = request.form.get('name') 
    company = request.form.get('Company')  
    industry = request.form.get('Industry') 
    budget = request.form.get('Budget')
                        
    sponsor.username = name
    sponsor.CompanyName = company
    sponsor.Industry = industry
    sponsor.Budget = budget
    db.session.commit()
    flash('Account updated successfully.')

    return render_template('sponsor/profile.html', sponsor=sponsor)

@app.route('/campaign/add')
@sponsor_req
def add_campaign():
    return render_template('campaign/add.html')

@app.route('/campaign/add', methods=['POST'])
@sponsor_req
def add_campaign_post():
    name = request.form.get('name')
    description = request.form.get('description')
    startdate_str = request.form.get('startdate')
    enddate_str = request.form.get('enddate')
    startdate = datetime.strptime(startdate_str, '%Y-%m-%d').date()
    enddate = datetime.strptime(enddate_str, '%Y-%m-%d').date()
    budget = request.form.get('budget')
    goal= request.form.get('goal')
    visibility_str = request.form.get('visibility')
    visibility = True if visibility_str == 'on' else False

    if not name or not description or not startdate or not enddate or not budget or not goal or not visibility:
        flash('Please fill out all the required details.')
        return redirect(url_for('add_campaign'))
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    if user:
        sponsor_name = user.username
        sponsor = Sponsor.query.filter_by(username=sponsor_name).first()
        if sponsor:
            campaign = Campaign(SponsorId=sponsor.id, Name=name, Description=description, StartDate=startdate, EndDate=enddate, Budget=budget, Goals=goal, Visibility=visibility)
            db.session.add(campaign)
            db.session.commit()
        else:
            flash('Sponsor not found.')
            return redirect(url_for('add_campaign'))
    else:
        flash('User not found.')
        return redirect(url_for('add_campaign'))
    
    user = User.query.get(session['user_id'])
    sponsor = Sponsor.query.filter_by(username=user.username).first()
    return redirect(url_for('sponsor',  sponsor_id = sponsor.id))

@app.route('/campaign/<int:id>')
@sponsor_req
def show_campaign(id):
    campaign = Campaign.query.get(id)
    if not campaign:
         flash('Camapign does not exist.')
         return redirect(url_for('sponsor', sponsor_id=campaign.SponsorId))
    return render_template('campaign/show.html', campaign=campaign)

@app.route('/campaign/<int:id>/edit')
@sponsor_req
def edit_campaign(id):
    campaign = Campaign.query.get(id)
    if not campaign:
        flash('Camapign does not exist.')
        return redirect(url_for('sponsor'))
    return render_template('campaign/edit.html', campaign=campaign)

@app.route('/campaign/<int:id>/edit', methods=['POST'])
@sponsor_req
def edit_campaign_post(id):
    campaign = Campaign.query.get(id)
    if not campaign:
        flash('Camapign does not exist.')
        return redirect(url_for('sponsor'))
    
    name = request.form.get('name')
    description = request.form.get('description')
    startdate_str = request.form.get('startdate')
    enddate_str = request.form.get('enddate')
    startdate = datetime.strptime(startdate_str, '%Y-%m-%d').date()
    enddate = datetime.strptime(enddate_str, '%Y-%m-%d').date()
    budget = request.form.get('budget')
    goal= request.form.get('goal')
    visibility_str = request.form.get('visibility')
    visibility = True if visibility_str == 'on' else False

    campaign.Name = name
    campaign.Description = description
    campaign.StartDate = startdate
    campaign.EndDate = enddate
    campaign.Budget = budget
    campaign.Goals = goal
    campaign.Visibility = visibility
    db.session.commit()

    flash('Campaign updated successfully.')
    user = User.query.get(session['user_id'])
    sponsor = Sponsor.query.filter_by(username=user.username).first()
    return redirect(url_for('sponsor',  sponsor_id = sponsor.id))

@app.route('/campaign/<int:id>/delete')
@sponsor_req
def delete_campaign(id):
    campaign = Campaign.query.get(id)
    if not campaign:
        flash('Campaign does not exist.')
        return redirect(url_for('sponsor'))
    return render_template('campaign/delete.html' , campaign = campaign)

@app.route('/campaign/<int:id>/delete', methods=['POST'])
@sponsor_req
def delete_campaign_post(id):
    campaign = Campaign.query.get(id)
    if not campaign:
        flash('Campaign does not exist.')
        return redirect(url_for('sponsor'))
    db.session.delete(campaign)
    db.session.commit()

    flash('Campaign deleted successfully.')
    user = User.query.get(session['user_id'])
    sponsor = Sponsor.query.filter_by(username=user.username).first()
    return redirect(url_for('sponsor',  sponsor_id = sponsor.id))

@app.route('/adreq/add/<int:campaign_id>')
@sponsor_req
def add_adreq(campaign_id):
    campaigns = Campaign.query.all()
    campaign= Campaign.query.get(campaign_id)
    if not campaign:
        flash('Campaign doent not exist.')
        return redirect(url_for('sponsor'))
    return render_template('AdReq/add.html', campaign=campaign, campaigns=campaigns)

@app.route('/adreq/add', methods=['POST'])
@sponsor_req
def add_adreq_post():
    message = request.form.get('Message')
    campaign_id = request.form.get('campaign_id')
    requirement = request.form.get('Requirement')
    pay = request.form.get('PaymentAmount')
    visibility_str = request.form.get('Status')
    status = True if visibility_str == 'on' else False

    campaign = Campaign.query.get(campaign_id)

    if not message or not requirement or not pay or not status:
        flash('Please fill out all the required details.')
        return redirect(url_for('add_adreq', campaign_id=campaign_id))
    
    if not campaign:
        flash('Campaign not found.')
        return redirect( url_for('add_adreq', campaign_id=campaign_id))
        
    adreq = Adrequest(CampaignId=campaign_id, Messages=message, Requirements=requirement, PaymentAmount=pay,  Status=status)
    db.session.add(adreq)
    db.session.commit()

    flash('Ad request added successfully.')
    return redirect(url_for('show_campaign', id=campaign_id))

@app.route('/adreq/<int:campaign_id>/edit/<int:id>')
@sponsor_req
def edit_adreq(campaign_id, id):
    campaign = Campaign.query.get(campaign_id)
    adreq = Adrequest.query.get(id)
    return render_template('AdReq/edit.html', campaign=campaign, adreq=adreq)

@app.route('/adreq/edit/<int:id>', methods=['POST'])
@sponsor_req
def edit_adreq_post(id):
    adreq= Adrequest.query.get(id)

    campaign_id = request.form.get('campaign_id')
    message = request.form.get('Message') or adreq.Messages
     
    requirement = request.form.get('Requirement') or adreq.Requirements
    pay = request.form.get('PaymentAmount')  or adreq.PaymentAmount
    visibility_str = request.form.get('Status')  or adreq.Status
    status = True if visibility_str == 'on' else False

    campaign = Campaign.query.get(campaign_id)
    adreq= Adrequest.query.get(id)
    
    if not campaign:
        flash('Campaign not found.')
        return redirect( url_for('add_adreq', campaign_id=campaign_id))

    adreq.Messages = message
    adreq.Requirements = requirement
    adreq.PaymentAmount = pay
    adreq.Status = status
    db.session.commit()

    flash('Ad request updates successfully.')
    return redirect(url_for('show_campaign', id=campaign_id))

@app.route('/adreq/<int:campaign_id>/delete/<int:id>')
@sponsor_req
def delete_adreq(id,campaign_id):
    adreq = Adrequest.query.get(id)
    campaign = Campaign.query.get(campaign_id)
    campaign_id = campaign.id
    if not adreq:
        flash('Product does not exist')
        return redirect(url_for('add_adreq', campaign_id=campaign_id))
    return render_template('AdReq/delete.html')

@app.route('/adreq/<int:campaign_id>/delete/<int:id>', methods=['POST'])
@sponsor_req
def delete_adreq_post(id,campaign_id):
    adreq = Adrequest.query.get(id)
    campaign = Campaign.query.get(campaign_id)
    campaign_id = campaign.id
    if not adreq:
        flash('AdRequest does not exist')
        return redirect(url_for('add_adreq', campaign_id=campaign_id))

    db.session.delete(adreq)
    db.session.commit()

    flash('Ad Request deleted successfully')
    return redirect(url_for('show_campaign', id=campaign_id))

@app.route('/sponsor/accept_application/<int:application_id>', methods=['POST'])
@sponsor_req
def accept_application(application_id):
    application = Application.query.get(application_id)
    application.Approval = True
    db.session.commit()

    flash('Request accepted successfully.')
    user = User.query.get(session['user_id'])
    sponsor = Sponsor.query.filter_by(username=user.username).first()
    return redirect(url_for('sponsor',  sponsor_id = sponsor.id))

@app.route('/sponsor/reject_application/<int:application_id>', methods=['POST'])
@sponsor_req
def reject_application(application_id):
    application = Application.query.get(application_id)
    db.session.delete(application)
    db.session.commit()

    flash('Request rejected.')
    user = User.query.get(session['user_id'])
    sponsor = Sponsor.query.filter_by(username=user.username).first()
    return redirect(url_for('sponsor',  sponsor_id = sponsor.id))

@app.route('/sponsor/send_request/<int:inf_id>', methods=['POST'])
@sponsor_req
def send_request(inf_id):
    influencer = Influencer.query.get(inf_id)
    user = User.query.get(session['user_id'])    
    sponsor = Sponsor.query.filter_by(username=user.username).first()
    req = Request(InfluencerId = influencer.id, SponsorId= sponsor.id, AdReqId=sponsor.id, Acceptance=False)
    db.session.add(req)
    db.session.commit()
    return redirect(url_for('sponsor',  sponsor_id = sponsor.id))

@app.route('/sponsor/work/<int:id>')
@sponsor_req
def work(id):
    payment = Payment.query.filter_by(SponsorId=id)
    return render_template('sponsor/Work.html', payments=payment)

@app.route('/sponsor/payment/<int:id>')
@sponsor_req
def payment(id):
    payment = Payment.query.get(id)
    influencer = Influencer.query.get(payment.InfluencerId)    
    return render_template('sponsor/payment.html', payments=payment, influencer=influencer)

@app.route('/sponsor/payment/<int:id>', methods=['POST'])
@sponsor_req
def payment_post(id):
    payment = Payment.query.get(id)
    payment.Payed = True
    db.session.commit()

    flash('Payment done successfully.')
    return redirect(url_for('work', id=payment.SponsorId))


# _______________________INFLUENCER PAGES________________________

@app.route('/influencer/<int:influencer_id>')
@influencer_req
def influencer(influencer_id): 
    influencer = Influencer.query.get(influencer_id)

    if influencer.Flag==True:
        flash('You are flagged by the Admin.')
        return redirect(url_for('login'))
    
    adreq = Adrequest.query.all()
    campaign = Campaign.query.all()

    cname = request.args.get('cname') or ''
    iname = request.args.get('iname') or ''
    price = request.args.get('price')
    
    if price:
        try:
            price = float(price)
        except ValueError:
            flash('Invalid price')
            return redirect(url_for('index'))
        if price <= 0:
            flash('Invalid price')
            return redirect(url_for('index'))

    if cname:
        campaign = Campaign.query.join(Campaign.Sponsor).filter(Sponsor.CompanyName.ilike(f'%{cname}%')).all()

    if iname:
        campaign = Campaign.query.join(Campaign.Sponsor).filter(Sponsor.Industry.ilike(f'%{iname}%')).all()

    if not influencer:
            flash('influencer doen not exist.')
            return redirect(url_for('login'))
    
    req = Request.query.filter_by(InfluencerId=influencer_id)
    SponsorId = [r.SponsorId for r in req.all()]
    sponsors=Sponsor.query.filter(Sponsor.id.in_(SponsorId)).all()

    return render_template('influencer/home.html', sponsors=sponsors, campaign=campaign, adreq=adreq, influencer=influencer, cname=cname, iname=iname, price=price)


@app.route('/influencer')
def inf_home():
    user =  User.query.get(session['user_id'])
    inf = Influencer.query.filter_by(username=user.username).first()
    return redirect(url_for('influencer', influencer_id=inf.id))

@app.route('/influencer/adreq_info/<int:id>')
@auth_req
def campaign_info(id):
    campaign = Campaign.query.get(id)
    return render_template('campaign/info.html', campaign=campaign )

@app.route('/influencer/sponsor_info/<int:id>')
@auth_req
def sponsor_info(id):
    sponsor = Sponsor.query.get(id)
    campaign = Campaign.query.filter_by(SponsorId=sponsor.id)
    return render_template('sponsor/info.html', sponsor=sponsor , campaign=campaign)

@app.route('/influencer/req_sponsor_info/<int:id>', methods=['POST'])
@influencer_req
def req_sponsor_info(id):
    user = User.query.get(session['user_id'])
    influencer = Influencer.query.filter_by(username=user.username).first()
    reqs = Request.query.filter_by(SponsorId=id, InfluencerId=influencer.id)  
    for req in reqs:
        db.session.delete(req)
    db.session.commit()
    return redirect(url_for('sponsor_info', id=id))

@app.route('/influencer/<int:influencer_id>/delete')
@influencer_req
def influencer_delete(influencer_id): 
    influencer = Influencer.query.get(influencer_id)
    if not influencer:
        flash('Influencer does not exist.')
        return redirect(url_for('login'))

    return render_template('influencer/delete.html', influencer=influencer)

@app.route('/influencer/<int:influencer_id>/delete', methods=['POST'])
@influencer_req
def influencer_delete_post(influencer_id): 
    influencer = Influencer.query.get(influencer_id)
    user = User.query.filter_by(username=influencer.username).first()
    if not influencer:
        flash('Influencer does not exist.')
        return redirect(url_for('login'))
    db.session.delete(influencer)
    db.session.delete(user)
    db.session.commit()

    flash('Account deleted successfully.')
    return redirect(url_for('login'))

@app.route('/influencer/<int:influencer_id>/update')
@influencer_req
def influencer_update(influencer_id):
    influencer = Influencer.query.get(influencer_id)
    if not influencer:
        flash('influencer does not exist.')
        return redirect(url_for('login'))
    
    return render_template('influencer/update.html', influencer=influencer)

@app.route('/influencer/<int:influencer_id>/update', methods=['POST'])
@influencer_req
def influencer_update_post(influencer_id):
    influencer = Influencer.query.get(influencer_id)
    if not influencer:
        flash('influencer does not exist.')
        return redirect(url_for('login'))
        
    name = request.form.get('name') 
    company = request.form.get('Niche')  
    industry = request.form.get('Category') 
    budget = request.form.get('Reach')
                        
    influencer.username = name
    influencer.Niche = company
    influencer.Category = industry
    influencer.Reach = budget
    db.session.commit()
    flash('Account updated successfully.')

    return render_template('influencer/profile.html', influencer=influencer)

@app.route('/influencer/application/<int:id>')
@influencer_req
def apply(id):
    adreq = Adrequest.query.get(id)
    return render_template('influencer/apply.html', adreq=adreq)

@app.route('/influencer/application', methods=['POST'])
@influencer_req
def apply_post():
    message = request.form.get('description')
    payask = request.form.get('budget')
    adreq = request.form.get('adreq_id')
    adrequest = Adrequest.query.get(adreq)

    user_id = session['user_id']
    user = User.query.get(user_id)
    if user:
        inf_name = user.username
        influencer = Influencer.query.filter_by(username=inf_name).first()
    
    application = Application(InfluencerId=influencer.id ,SponsorId= adrequest.Campaign.SponsorId ,AdReqId= adrequest.id ,Message=message,PayAsk=payask ,Approval=False)
    db.session.add(application)
    db.session.commit()

    return redirect(url_for('campaign_info', id = adrequest.Campaign.id))

@app.route('/influencer/delete/<int:id>', methods=['POST'])
@influencer_req
def delete_request(id):
    user = User.query.get(session['user_id'])
    influencer = Influencer.query.filter_by(username=user.username).first()
    reqs = Request.query.filter_by(SponsorId=id, InfluencerId=influencer.id)  
    for req in reqs:
        db.session.delete(req)
    db.session.commit()

    return redirect(url_for('influencer', influencer_id = influencer.id))

@app.route('/influencer/manage_ad/<int:influencer_id>')
@influencer_req
def manage_ads(influencer_id):
    application = Application.query.filter_by(InfluencerId = influencer_id)
    approved = [app for app in application if app.Approval == True]
    pending = [app for app in application if app.Approval == False]
    return render_template('/influencer/manage.html', approved=approved, pendings=pending)

@app.route('/influencer/handover/<int:id>')
@influencer_req
def handover(id):
    application = Application.query.get(id)
    return render_template('influencer/handover.html', application=application)

@app.route('/influencer/handover/<int:id>', methods=['POST'])
@influencer_req
def handover_post(id):
    application = Application.query.get(id)

    InfluencerId = application.InfluencerId
    SponsorId = application.SponsorId
    AdReqId = application.AdReqId
    Pay=application.PayAsk
    Work = request.form.get('link')

    payment = Payment(InfluencerId=InfluencerId,SponsorId=SponsorId,AdReqId=AdReqId,Pay=Pay,Work=Work,Payed=False)
    db.session.add(payment)
    db.session.delete(application)
    db.session.commit()

    return redirect(url_for('manage_ads', influencer_id = application.InfluencerId))

@app.route('/influencer/payment/<int:id>')
@influencer_req
def inf_pay(id):
    payments = Payment.query.filter_by(InfluencerId=id)
    return render_template('influencer/payment.html', payments=payments)

# _______________________ ADMIN PAGES________________________

@app.route('/admin')
@admin_req
def admin():
    sponsors =Sponsor.query.all()
    sponsor_industry = list({sponsor.Industry for sponsor in sponsors})
    no_of_campaign_per_industry = {industry: sum(len(sponsor.Campaigns) for sponsor in sponsors if sponsor.Industry == industry) for industry in sponsor_industry}
    
    influencers =Influencer.query.all()
    inf_niche = list({influencer.Niche for influencer in influencers})   
    no_of_application_per_inf_niche = {niche: sum(len(influencer.Applications01) for influencer in influencers if influencer.Niche == niche) for niche in inf_niche}    
    return render_template('Admin/home.html',sponsor_industry=sponsor_industry,no_of_campaign_per_industry=no_of_campaign_per_industry,inf_niche=inf_niche,no_of_application_per_inf_niche=no_of_application_per_inf_niche)


@app.route('/admin/influencers')
@admin_req
def admin_inf():
    influencer=Influencer.query.all()
    return render_template('admin/influencer.html', influencer=influencer)


@app.route('/admin/influencers/<int:id>', methods=['POST'])
@admin_req
def inf_flag(id):
    inf = Influencer.query.get(id)

    if inf:
        if inf.Flag:
            inf.Flag = False
            flash('Influencer un-flagged.')
        else:
            inf.Flag = True
            flash('Influencer flagged.')
        db.session.commit()
    else:
        flash('Influencer not found.')

    return redirect(url_for('admin_inf'))

@app.route('/admin/influencers/removes/<int:id>', methods=['POST'])
@admin_req
def inf_remove(id):
    inf=Influencer.query.get(id)
    db.session.delete(inf)
    db.session.commit()

    flash('Influencer removed from platform.')
    return redirect(url_for('admin_inf'))


@app.route('/admin/sponsor')
@admin_req
def admin_spn():
    sponsor=Sponsor.query.all()
    return render_template('admin/sponsor.html', sponsor=sponsor)


@app.route('/admin/sponsor/<int:id>', methods=['POST'])
@admin_req
def spn_flag(id):
    spn = Sponsor.query.get(id)

    if spn:
        if spn.Flag:
            spn.Flag = False
            flash('Sponsor un-flagged.')
        else:
            spn.Flag = True
            flash('Sponsor flagged.')
        db.session.commit()
    else:
        flash('Sponsor not found.')

    return redirect(url_for('admin_spn'))

@app.route('/admin/sponsor/remove/<int:id>', methods=['POST'])
@admin_req
def spn_remove(id):
    spn=Sponsor.query.get(id)
    db.session.delete(spn)
    db.session.commit()

    flash('Sponsor removed from platform.')
    return redirect(url_for('admin_spn'))