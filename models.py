from app import app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, delete
from werkzeug.security import generate_password_hash

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True)
    passhash = db.Column(db.String(256), nullable=False)
    Role = db.Column(db.String(32), nullable=False)

    Admins = db.relationship('Admin', backref = 'User', lazy = True)
    Influencers = db.relationship('Influencer', backref = 'User', lazy = True)
    Sponsors = db.relationship('Sponsor', backref = 'User', lazy = True)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), ForeignKey('user.username'), unique=True)

class Influencer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), ForeignKey('user.username'), unique=True)
    Niche = db.Column(db.String(64), nullable=False)
    Category = db.Column(db.String(64), nullable=False)
    Reach = db.Column(db.Integer, nullable=True, default=0)
    Flag = db.Column(db.Boolean, nullable=False)

    Applications01 = db.relationship('Application', backref = 'Influencer', lazy = True)
    Payments01 = db.relationship('Payment', backref = 'Influencer', lazy = True)
    Requests01 = db.relationship('Request', backref = 'Influencer', lazy = True)

    
class Sponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), ForeignKey('user.username'), unique=True)
    CompanyName = db.Column(db.String(64), nullable=False)
    Industry = db.Column(db.String(64), nullable=False)
    Budget = db.Column(db.Integer, nullable=True, default=0)
    Flag = db.Column(db.Boolean, nullable=False)


    Campaigns = db.relationship('Campaign', backref = 'Sponsor', lazy = True, cascade='all,delete-orphan')
    Applications02 = db.relationship('Application', backref = 'Sponsor', lazy = True)
    Payments02 = db.relationship('Payment', backref = 'Sponsor', lazy = True)
    Requests02 = db.relationship('Request', backref = 'Sponsor', lazy = True)

    
class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    SponsorId = db.Column(db.String(32), ForeignKey('sponsor.id'), unique=False)
    Name = db.Column(db.String(32), nullable=False)
    Description = db.Column(db.String(256), nullable=False)
    StartDate = db.Column(db.Date, nullable=False)
    EndDate = db.Column(db.Date, nullable=False)
    Budget = db.Column(db.Integer, nullable=False)
    Visibility = db.Column(db.Boolean, nullable=False)
    Goals = db.Column(db.String(256), nullable=False)

    AdRequests = db.relationship('Adrequest', backref = 'Campaign', lazy = True, cascade='all, delete-orphan')

class Adrequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    CampaignId = db.Column(db.String(32), ForeignKey('campaign.id'), unique=False)
    Messages = db.Column(db.String(256), nullable=False)
    Requirements = db.Column(db.String(256), nullable=False)
    PaymentAmount = db.Column(db.Integer, nullable=False)
    Status = db.Column(db.Boolean, nullable=False)

    Applications03 = db.relationship('Application', backref = 'Adrequest', lazy = True, cascade='all, delete-orphan')
    Payments03 = db.relationship('Payment', backref = 'Adrequest', lazy = True)
    Requests03 = db.relationship('Request', backref = 'Adrequest', lazy = True)

class Application(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    InfluencerId = db.Column(db.String(32), ForeignKey('influencer.id'), unique=False)
    SponsorId = db.Column(db.String(32), ForeignKey('sponsor.id'), unique=False)
    AdReqId = db.Column(db.String(32), ForeignKey('adrequest.id'), unique=False)
    Message = db.Column(db.String(256), nullable=False)
    PayAsk = db.Column(db.Integer, nullable=False)
    Approval = db.Column(db.Boolean, nullable=False)

class Payment(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    InfluencerId = db.Column(db.String(32), ForeignKey('influencer.id'), unique=False)
    SponsorId = db.Column(db.String(32), ForeignKey('sponsor.id'), unique=False)
    AdReqId = db.Column(db.String(32), ForeignKey('adrequest.id'), unique=False)
    Pay = db.Column(db.Integer, nullable=False)
    Work = db.Column(db.String(256), nullable=False)
    Payed = db.Column(db.Boolean, nullable=False)

class Request(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    InfluencerId = db.Column(db.String(32), ForeignKey('influencer.id'), unique=False)
    SponsorId = db.Column(db.String(32), ForeignKey('sponsor.id'), unique=False)
    AdReqId = db.Column(db.String(32), ForeignKey('adrequest.id'), unique=False)
    Acceptance = db.Column(db.Boolean, nullable=False)

with app.app_context():
    db.create_all()

    admin = User.query.filter_by(Role='Admin').first()
    if not admin:
        password_hash = generate_password_hash('admin123')
        admin = User(username = 'admin', passhash = password_hash, Role = 'Admin')
        adminn = Admin(username = 'admin')
        db.session.add(admin)
        db.session.add(adminn)
        db.session.commit()
