from flask import Flask, render_template, request, redirect, session, flash, url_for
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
load_dotenv()
from sqlalchemy import func

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI' ] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS' ] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

db = SQLAlchemy(app)

#Models
class Users(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, nullable = False, default = False)
    is_customer = db.Column(db.Boolean, nullable = False, default = False)
    is_professional = db.Column(db.Boolean, nullable = False, default = False)
    name = db.Column(db.String(20))
    date_created = db.Column(db.DateTime)
    
    def __repr__(self):
        return f"User('{self.user_id}', '{self.name}', '{self.username}')"

class ServiceProfessionals(db.Model):
    __tablename__ = "serviceprofessionals"
    professional_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    service_type = db.Column(db.String(50), nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    profile_verified = db.Column(db.Boolean, nullable=False)
    avg_rating = db.Column(db.Float, nullable=False)
    total_reviews = db.Column(db.Integer, nullable=False)

    user = db.relationship('Users', backref='professional', lazy=True)

    def __repr__(self):
        return f"ServiceProfessional('{self.user.username}', '{self.service_type}', '{self.avg_rating}')"

class Customers(db.Model):
    __tablename__ = "customers"
    customer_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)

    user = db.relationship('Users', backref='customer', lazy=True)

    def __repr__(self):
        return f"Customer('{self.user.username}', '{self.address}', '{self.pin_code}')"

class Services(db.Model):
    __tablename__ = "services"
    service_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Service('{self.name}', '{self.base_price}')"

class ServiceRequests(db.Model):
    __tablename__ = "servicerequests"
    service_request_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.service_id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('serviceprofessionals.professional_id'), nullable=False)
    date_of_request = db.Column(db.DateTime, nullable=False)
    date_of_completion = db.Column(db.DateTime)
    status = db.Column(db.String(50), nullable=False)
    remarks = db.Column(db.Text)
    preferred_date = db.Column(db.DateTime, nullable=False)
    preferred_time = db.Column(db.String(20), nullable=False)
    service_address = db.Column(db.String(200), nullable=False)
    service_pin_code = db.Column(db.String(10), nullable=False)
    special_instructions = db.Column(db.Text)

    customer = db.relationship('Customers', backref='service_requests', lazy=True)
    service = db.relationship('Services', backref='service_requests', lazy=True)
    professional = db.relationship('ServiceProfessionals', backref='service_requests', lazy=True)

    def __repr__(self):
        return f"ServiceRequest('{self.customer.user.username}', '{self.service.name}', '{self.status}')"

class Reviews(db.Model):
    review_id = db.Column(db.Integer, primary_key=True)
    service_request_id = db.Column(db.Integer, db.ForeignKey('servicerequests.service_request_id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('serviceprofessionals.professional_id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.Text)

    service_request = db.relationship('ServiceRequests', backref='reviews', lazy=True)
    professional = db.relationship('ServiceProfessionals', backref='reviews', lazy=True)

    def __repr__(self):
        return f"Review('{self.professional.user.username}', '{self.rating}', '{self.review_text}')"

with app.app_context():
    db.create_all()

#Routes 
    
@app.route("/")
def home():
    return render_template("home.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        print(f"Login attempt - Username: {username}")
        
        user = Users.query.filter_by(username=username).first()
        
        if not user:
            print("No user found with this username")
            flash('Invalid username or password')
            return redirect(url_for('login'))
        
        if user.password != password:
            print(f"Password mismatch for user {username}")
            flash('Invalid username or password')
            return redirect(url_for('login'))
        
        session['user_id'] = user.user_id
        session['is_admin'] = user.is_admin
        session['is_customer'] = user.is_customer
        session['is_professional'] = user.is_professional
        
        print(f"User found: Admin: {user.is_admin}, Customer: {user.is_customer}, Professional: {user.is_professional}")
        
        if user.is_admin:
            print("Redirecting to admin dashboard")
            return redirect(url_for('admin_dashboard'))
        elif user.is_customer:
            customer = Customers.query.filter_by(user_id=user.user_id).first()
            if not customer:
                flash('Customer profile not found. Please contact support.')
                return redirect(url_for('login'))
            return redirect(url_for('customer_dashboard'))
        elif user.is_professional:
            return redirect(url_for('professional_dashboard'))
        
        flash('No user role assigned. Please contact support.')
        return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/register_choice')
def register_choice():
    return render_template('register_choice.html')

@app.route('/register/customer', methods=['GET', 'POST'])
def register_customer():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        address = request.form['address']
        pin_code = request.form['pin_code']
        
        if not all([username, password, name, address, pin_code]):
            flash('All fields are required')
            return redirect(url_for('register_customer'))
        
        existing_user = Users.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists')
            return redirect(url_for('register_customer'))
        
        try:
            user = Users(
                username=username,
                password=password, 
                name=name,
                is_admin=False,
                is_customer=True,
                is_professional=False,
                date_created=datetime.utcnow()
            )
            
            db.session.add(user)
            db.session.flush()
            
            customer = Customers(
                user_id=user.user_id,
                address=address,
                pin_code=pin_code
            )
            
            db.session.add(customer)
            db.session.commit()
            
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
        
        except Exception as e:
            db.session.rollback()
            print(f"Registration error: {e}")
            flash('An error occurred during registration. Please try again.')
            return redirect(url_for('register_customer'))
    
    return render_template('register_customer.html')

@app.route('/register/professional', methods=['GET', 'POST'])
def register_professional():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        
        if Users.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register_professional'))
        
        user = Users(
            username=username,
            password=password,  
            name=name,
            is_admin=False,
            is_customer=False,
            is_professional=True,
            date_created=datetime.utcnow()
        )
        
        db.session.add(user)
        db.session.commit()
        
        professional = ServiceProfessionals(
            user_id=user.user_id,
            service_type=request.form['service_type'],
            experience=int(request.form['experience']),
            profile_verified=False,
            avg_rating=0.0,
            total_reviews=0
        )
        db.session.add(professional)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register_professional.html')

#Admin routes

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    total_professionals = ServiceProfessionals.query.count()
    verified_professionals = ServiceProfessionals.query.filter_by(profile_verified=True).count()
    total_professional_reviews = Reviews.query.count()
    
    print(f"Total Professionals: {total_professionals}")
    print(f"Verified Professionals: {verified_professionals}")
    
    avg_professional_rating = (db.session.query(func.avg(Reviews.rating))
                                .filter(Reviews.rating.isnot(None))
                                .scalar() or 0.0)
    print(f"Average Professional Rating: {avg_professional_rating}")
    
    unverified_professionals_count = ServiceProfessionals.query.filter_by(profile_verified=False).count()
    
    services = Services.query.all()
    professionals = ServiceProfessionals.query.all()
    customers = Customers.query.all()
    
    return render_template('admin_dashboard.html', 
                           services=services, 
                           professionals=professionals, 
                           customers=customers, 
                           avg_professional_rating=avg_professional_rating,
                           total_professionals=total_professionals,
                           verified_professionals=verified_professionals,
                           total_professional_reviews=total_professional_reviews,
                           unverified_professionals_count=unverified_professionals_count)

@app.route('/admin/services', methods=['GET', 'POST'])
def veiw_services():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        service_id = request.form.get('service_id')
        service = Services.query.get(service_id)
        
        if service:
            existing_requests = ServiceRequests.query.filter_by(service_id=service_id).first()
            
            if existing_requests:
                flash('Cannot delete service - it is currently in use in existing service requests.')
            else:
                db.session.delete(service)
                db.session.commit()
                flash('Service deleted successfully!')
        else:
            flash('Service not found.')
        
        return redirect(url_for('veiw_services'))
    
    services = Services.query.all()
    return render_template('view_services(admin).html', services=services)
    
@app.route('/admin/services/edit/<int:service_id>', methods=['GET', 'POST'])
def edit_service(service_id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    service = Services.query.get_or_404(service_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        base_price = request.form.get('base_price')
        description = request.form.get('description')
        
        if not name or not base_price:
            flash('Service name and base price are required.', 'error')
            return render_template('edit_service.html', service=service)
        
        try:
            service.name = name
            service.base_price = float(base_price)
            service.description = description
            
            db.session.commit()
            flash('Service updated successfully!', 'success')
            return redirect(url_for('veiw_services'))
        
        except ValueError:
            flash('Invalid base price. Please enter a valid number.', 'error')
            return render_template('edit_service.html', service=service)
    
    return render_template('edit_service(admin).html', service=service)

@app.route('/admin/services/new', methods=['GET', 'POST'])
def create_service():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        service = Services(
            name=request.form['name'],
            base_price=float(request.form['base_price']),
            description=request.form['description']
        )
        db.session.add(service)
        db.session.commit()
        flash('Service created successfully!')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('add_service(admin).html')

@app.route('/admin/professionals/unverified')
def unverified_professionals():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    unverified_professionals = ServiceProfessionals.query.filter_by(profile_verified=False).all()
    return render_template('unverified_professionals.html', professionals=unverified_professionals)

@app.route('/admin/professional/<int:professional_id>/verify')
def verify_professional(professional_id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    professional = ServiceProfessionals.query.get_or_404(professional_id)
    professional.profile_verified = True
    db.session.commit()
    
    flash(f'Professional {professional.user.name} has been verified successfully!')
    return redirect(url_for('unverified_professionals'))

@app.route('/admin/professional/<int:professional_id>/reject', methods=['POST'])
def reject_professional(professional_id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
   
    professional = ServiceProfessionals.query.get_or_404(professional_id)
   
    user_name = professional.user.name  
    user_id = professional.user_id      
  
    db.session.delete(professional)
    
    user = Users.query.get(user_id)  
    if user:
        db.session.delete(user)
    
    db.session.commit()
    
    flash(f'Professional {user_name} has been rejected and removed.')
    return redirect(url_for('unverified_professionals'))

@app.route('/admin/users')
def manage_users():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    customers = Customers.query.join(Users).all()
    professionals = ServiceProfessionals.query.join(Users).all()
    
    return render_template('manage_users(admin).html', 
                           customers=customers, 
                           professionals=professionals)

@app.route('/admin/user/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    user = Users.query.get_or_404(user_id)
    
    try:
        if user.is_customer:
            Customers.query.filter_by(user_id=user_id).delete()
        elif user.is_professional:
            ServiceProfessionals.query.filter_by(user_id=user_id).delete()
    
        db.session.delete(user)
        db.session.commit()
        
        flash(f'User {user.username} has been deleted successfully.')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {str(e)}')
    
    return redirect(url_for('manage_users'))

@app.route('/admin/search/customers', methods=['GET', 'POST'])
def admin_search_customers():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    customers = Customers.query.all()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        pin_code = request.form.get('pin_code', '').strip()

        query = Customers.query.join(Users)
        
        if name:
            query = query.filter(Users.name.ilike(f'%{name}%'))
        
        if pin_code:
            query = query.filter(Customers.pin_code.ilike(f'%{pin_code}%'))
        
        customers = query.all()
    
    return render_template('admin_search_customers.html', customers=customers)

@app.route('/admin/service-requests')
def admin_service_requests():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    status = request.args.get('status', '')
    customer_name = request.args.get('customer_name', '')
    professional_name = request.args.get('professional_name', '')
    
    query = ServiceRequests.query
    
    if status:
        query = query.filter_by(status=status)
    
    if customer_name:
        query = query.join(Customers).join(Customers.user)\
            .filter(Users.name.ilike(f'%{customer_name}%'))
    
    if professional_name:
        query = query.join(ServiceProfessionals).join(ServiceProfessionals.user)\
            .filter(Users.name.ilike(f'%{professional_name}%'))
    
    service_requests = query.all()
    
    return render_template('admin_service_requests.html', 
                           service_requests=service_requests)

@app.route('/admin/search/professionals', methods=['GET', 'POST'])
def admin_search_professionals():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    professionals = ServiceProfessionals.query.all()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        service_type = request.form.get('service_type', '').strip()
        min_experience = request.form.get('min_experience')
        verification_status = request.form.get('verification_status')
        
        query = ServiceProfessionals.query
        
        if name:
            query = query.join(Users).filter(Users.name.ilike(f'%{name}%'))
        
        if service_type:
            query = query.filter(ServiceProfessionals.service_type.ilike(f'%{service_type}%'))
        
        if min_experience:
            query = query.filter(ServiceProfessionals.experience >= int(min_experience))
        
        if verification_status:
            is_verified = verification_status == 'verified'
            query = query.filter(ServiceProfessionals.profile_verified == is_verified)
        
        professionals = query.all()
    
    return render_template('admin_search_professionals.html', professionals=professionals)



# Customer routes
@app.route('/customer/dashboard')
def customer_dashboard():
    if not session.get('is_customer'):
        return redirect(url_for('login'))
    
    try:
        customer = Customers.query.filter_by(user_id=session['user_id']).first()
        
        if not customer:
            flash('Customer profile not found. Please contact support.')
            return redirect(url_for('login'))
        
        service_requests = db.session.query(ServiceRequests).join(Services).join(ServiceProfessionals).filter(
            ServiceRequests.customer_id == customer.customer_id
        ).all()
        
        return render_template('customer_dashboard.html', 
                              customer=customer, 
                              service_requests=service_requests)
    
    except Exception as e:
        print(f"Error in customer dashboard: {e}")
        flash('An error occurred. Please try again.')
        return redirect(url_for('login'))
    
@app.route('/customer/profile', methods=['GET', 'POST'])
def customer_profile():
    if not session.get('is_customer'):
        return redirect(url_for('login'))
    
    customer = Customers.query.filter_by(user_id=session['user_id']).first()
    user = Users.query.get(session['user_id'])
    
    if request.method == 'POST':
        customer.address = request.form['address']
        customer.pin_code = request.form['pin_code']
        user.name = request.form['name']
        
        db.session.commit()
        flash('Profile updated successfully!')
        return redirect(url_for('customer_profile'))
    
    return render_template('customer_profile.html', customer=customer, user=user)

@app.route('/customer/service/search', methods=['GET', 'POST'])
def search_services():
    if not session.get('is_customer'):
        return redirect(url_for('login'))
    
    customer = Customers.query.filter_by(user_id=session['user_id']).first()

    services = Services.query.all()
    
    available_professionals = ServiceProfessionals.query.filter_by(profile_verified=True).all()
    
    if request.method == 'POST':
        service_name = request.form.get('service_name')
        pin_code = request.form.get('pin_code', customer.pin_code)
        min_price = request.form.get('min_price')
        max_price = request.form.get('max_price')
        
        # Build service query
        service_query = Services.query
        if service_name:
            service_query = service_query.filter(Services.name.ilike(f'%{service_name}%'))
        
        if min_price:
            service_query = service_query.filter(Services.base_price >= float(min_price))
        
        if max_price:
            service_query = service_query.filter(Services.base_price <= float(max_price))
        
        services = service_query.all()
        
        available_professionals = ServiceProfessionals.query.filter(
            ServiceProfessionals.profile_verified == True,
            ServiceProfessionals.service_type.ilike(f'%{service_name}%') if service_name else True
        ).all()
    
    return render_template('search_services.html', 
                           services=services, 
                           professionals=available_professionals,
                           customer_pin_code=customer.pin_code)

@app.route('/customer/book-service/<int:service_id>/<int:professional_id>', methods=['GET', 'POST'])
def book_service(service_id, professional_id):
    if not session.get('is_customer'):
        return redirect(url_for('login'))
    
    customer = Customers.query.filter_by(user_id=session['user_id']).first()
    service = Services.query.get_or_404(service_id)
    professional = ServiceProfessionals.query.get_or_404(professional_id)
    
    if request.method == 'POST':
        try:
            service_request = ServiceRequests(
                customer_id=customer.customer_id,
                service_id=service_id,
                professional_id=professional_id,
                date_of_request=datetime.utcnow(),
                status='requested',
                preferred_date=datetime.strptime(request.form['preferred_date'], '%Y-%m-%d'),
                preferred_time=request.form['preferred_time'],
                service_address=request.form.get('service_address', customer.address),
                service_pin_code=request.form.get('service_pin_code', customer.pin_code),
                special_instructions=request.form.get('special_instructions', '')
            )
            db.session.add(service_request)
            db.session.commit()
            
            flash('Service request created successfully!')
            return redirect(url_for('customer_dashboard'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating service request: {str(e)}')
    
    return render_template('book_service.html', 
                           service=service, 
                           professional=professional, 
                           customer=customer)

@app.route('/customer/service-requests/<int:request_id>')
def service_request_detail(request_id):
    if not session.get('is_customer'):
        return redirect(url_for('login'))
    
    customer = Customers.query.filter_by(user_id=session['user_id']).first()
    service_request = ServiceRequests.query.filter_by(
        customer_id=customer.customer_id, 
        service_request_id=request_id
    ).first_or_404()
    
    return render_template('service_request_detail.html', service_request=service_request)

@app.route('/customer/service-request/delete/<int:request_id>', methods=['GET'])
def delete_service_request(request_id):
    if not session.get('is_customer'):
        return redirect(url_for('login'))
    
    service_request = ServiceRequests.query.get_or_404(request_id)
    
    customer = Customers.query.filter_by(user_id=session['user_id']).first()
    if service_request.customer_id != customer.customer_id:
        flash('Unauthorized to delete this service request')
        return redirect(url_for('customer_dashboard'))
    
    if service_request.status in ['requested', 'assigned']:
        db.session.delete(service_request)
        db.session.commit()
        flash('Service request deleted successfully!')
    else:
        flash('Cannot delete a completed or closed service request')
    
    return redirect(url_for('customer_dashboard'))

@app.route('/customer/search/professionals', methods=['GET', 'POST'])
def customer_search_professionals():
    if not session.get('is_customer'):
        return redirect(url_for('login'))
    
    customer = Customers.query.filter_by(user_id=session['user_id']).first()
    
    professionals = ServiceProfessionals.query.filter_by(profile_verified=True).all()
    
    if request.method == 'POST':
        service_type = request.form.get('service_type', '').strip()
        min_rating = request.form.get('min_rating')
        pin_code = request.form.get('pin_code', customer.pin_code).strip()
        
        query = ServiceProfessionals.query.filter_by(profile_verified=True)
        
        if service_type:
            query = query.filter(ServiceProfessionals.service_type.ilike(f'%{service_type}%'))
        
        if min_rating:
            query = query.filter(ServiceProfessionals.avg_rating >= float(min_rating))
        
        professionals = query.all()
    
    return render_template('customer_search_professionals.html', 
                           professionals=professionals, 
                           customer_pin_code=pin_code)

# Professional routes
@app.route('/professional/dashboard')
def professional_dashboard():
    if not session.get('is_professional'):
        return redirect(url_for('login'))
    
    professional = ServiceProfessionals.query.filter_by(user_id=session['user_id']).first()
    
    if not professional.profile_verified:
        flash('Your profile is pending admin verification.')
        return redirect(url_for('logout'))
    
    status = request.args.get('status', '')
    if status:
        service_requests = ServiceRequests.query.filter_by(
            professional_id=professional.professional_id,
            status=status
        ).all()
    else:
        service_requests = ServiceRequests.query.filter_by(
            professional_id=professional.professional_id
        ).all()
    
    return render_template('service_professional_dashboard.html', 
                           professional=professional,
                           service_requests=service_requests,
                           recent_requests=service_requests)  

@app.route('/professional/service-requests')
def professional_service_requests():
    if not session.get('is_professional'):
        return redirect(url_for('login'))
    
    professional = ServiceProfessionals.query.filter_by(user_id=session['user_id']).first()
    
    status = request.args.get('status', '')
    
    query = ServiceRequests.query.filter_by(professional_id=professional.professional_id)
    
    if status:
        query = query.filter_by(status=status)
    
    service_requests = query.all()
    
    return render_template('professional_service_requests.html', 
                           service_requests=service_requests, 
                           professional=professional)

@app.route('/professional/request/<int:request_id>/<action>')
def handle_service_request(request_id, action):
    if not session.get('is_professional'):
        return redirect(url_for('login'))
    
    service_request = ServiceRequests.query.get_or_404(request_id)
    professional = ServiceProfessionals.query.filter_by(user_id=session['user_id']).first()
    
    if service_request.professional_id != professional.professional_id:
        flash('Unauthorized action')
        return redirect(url_for('professional_dashboard'))
    
    if action == 'accept':
        service_request.status = 'assigned'
    elif action == 'reject':
        service_request.status = 'rejected'
    elif action == 'complete':
        service_request.status = 'completed'
        service_request.date_of_completion = datetime.utcnow()
    
    db.session.commit()
    flash(f'Service request {action}ed successfully!')
    return redirect(url_for('professional_dashboard'))

@app.route('/professional/profile', methods=['GET', 'POST'])
def professional_profile():
    if not session.get('is_professional'):
        return redirect(url_for('login'))
    
    service_professional = ServiceProfessionals.query.filter_by(user_id=session['user_id']).first()
    user = Users.query.get(session['user_id'])
    
    if request.method == 'POST':
        service_professional.experience = request.form['experience']
        service_professional.service_type = request.form['service_type']
        user.name = request.form['name']
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('professional_profile'))

    return render_template('professional_profile.html', 
                           user=user, 
                           service_professional=service_professional)

# Review routes
@app.route('/customer/review/<int:request_id>', methods=['GET', 'POST'])
def create_review(request_id):
    if not session.get('is_customer'):
        return redirect(url_for('login'))
    
    service_request = ServiceRequests.query.get_or_404(request_id)
    
    if request.method == 'POST':
        review = Reviews(
            service_request_id=request_id,
            professional_id=service_request.professional_id,
            rating=int(request.form['rating']),
            review_text=request.form['review_text']
        )
        
        db.session.add(review)
        
        professional = service_request.professional
        professional.total_reviews += 1
        professional.avg_rating = (
            (professional.avg_rating * (professional.total_reviews - 1) + review.rating) 
            / professional.total_reviews
        )
        
        db.session.commit()
        flash('Review submitted successfully!')
        return redirect(url_for('customer_dashboard'))
    
    return render_template('create_review.html', service_request=service_request)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)