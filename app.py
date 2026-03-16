"""
RailBusAtithi - Flask Backend
Travel Booking Website for Hotels near Railway Stations and Bus Stands
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
import random
import secrets
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__)
app.secret_key = 'railbusatithi_secret_key_2024'

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Create upload folder if not exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
with app.app_context():
    db.create_all()
    
# ==================== DATABASE MODELS ====================

class User(db.Model):
    """User model for passengers, hotel owners, and admins"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # passenger, hotel_owner, admin
    phone = db.Column(db.String(20))
    city = db.Column(db.String(100))
    location = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reset_token = db.Column(db.String(200), nullable=True)
    
    # Relationships
    bookings = db.relationship('Booking', backref='user', lazy=True)
    hotels = db.relationship('Hotel', backref='owner', lazy=True)

class Hotel(db.Model):
    """Hotel model"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    near_station = db.Column(db.String(100))  # Nearest railway station
    near_bus_stop = db.Column(db.String(100))  # Nearest bus stop
    distance_station = db.Column(db.Float, default=1.0)  # Distance in km
    distance_bus = db.Column(db.Float, default=1.0)  # Distance in km
    price = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float, default=4.0)
    review_count = db.Column(db.Integer, default=0)
    total_rooms = db.Column(db.Integer, default=10)
    available_rooms = db.Column(db.Integer, default=10)
    amenities = db.Column(db.String(500))  # JSON string of amenities
    photos = db.Column(db.String(500))  # Comma-separated photo paths
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='hotel', lazy=True)

class Booking(db.Model):
    """Booking model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), nullable=False)
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    rooms = db.Column(db.Integer, default=1)
    guests = db.Column(db.Integer, default=1)
    total_price = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled, completed
    payment_method = db.Column(db.String(50))
    special_requests = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Review(db.Model):
    """Hotel review model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='reviews')

class Advertisement(db.Model):
    """Advertisement model"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    position = db.Column(db.String(50), nullable=False)  # homepage, search, hotel_detail, newsletter
    link = db.Column(db.String(500))
    impressions = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)
    budget = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='active')  # active, paused, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==================== HELPER FUNCTIONS ====================

def get_amenity_list(amenities_str):
    """Convert amenities string to list"""
    if amenities_str:
        return amenities_str.split(',')
    return []

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points (simplified)"""
    return round(random.uniform(0.5, 5.0), 1)

# ==================== PUBLIC ROUTES ====================

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/')
def index():
    """Home page with search and featured hotels"""
    # Get approved hotels for featured section
    featured_hotels = Hotel.query.filter_by(approved=True).limit(6).all()
    
    # Get popular destinations
    popular_cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 'Pune', 'Jaipur']
    
    return render_template('index.html', 
                         featured_hotels=featured_hotels,
                         popular_cities=popular_cities)

@app.route('/search')
def search():
    """Search hotels based on criteria"""
    city = request.args.get('city', '')
    near_type = request.args.get('near_type', 'station')  # station or bus
    check_in = request.args.get('check_in')
    check_out = request.args.get('check_out')
    
    query = Hotel.query.filter_by(approved=True)
    
    if city:
        query = query.filter(Hotel.city.ilike(f'%{city}%'))
    
    if near_type == 'station':
        if city:
            query = query.filter(Hotel.near_station.ilike(f'%{city}%'))
    else:
        if city:
            query = query.filter(Hotel.near_bus_stop.ilike(f'%{city}%'))
    
    hotels = query.all()
    
    # Add distance info (simulated)
    for hotel in hotels:
        hotel.distance = hotel.distance_station if near_type == 'station' else hotel.distance_bus
    
    return render_template('search_results.html', 
                         hotels=hotels, 
                         city=city, 
                         near_type=near_type,
                         check_in=check_in,
                         check_out=check_out)

@app.route('/hotel/<int:hotel_id>')
def hotel_detail(hotel_id):
    """Hotel detail page"""
    hotel = Hotel.query.get_or_404(hotel_id)
    reviews = Review.query.filter_by(hotel_id=hotel_id).order_by(Review.created_at.desc()).limit(10).all()
    
    amenities_list = get_amenity_list(hotel.amenities)
    photos_list = hotel.photos.split(',') if hotel.photos else []
    
    return render_template('hotel_detail.html', 
                         hotel=hotel, 
                         reviews=reviews,
                         amenities=amenities_list,
                         photos=photos_list)

# ==================== AUTH ROUTES ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_role'] = user.role
            
            # Redirect based on role
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'hotel_owner':
                return redirect(url_for('hotel_owner_dashboard'))
            else:
                return redirect(url_for('passenger_dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'passenger')
        phone = request.form.get('phone')
        city = request.form.get('city')
        location = request.form.get('location')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('register'))
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
        
        # Create new user
        hashed_password = generate_password_hash(password)
        new_user = User(
            name=name,
            email=email,
            password=hashed_password,
            role=role,
            phone=phone,
            city=city,
            location=location
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password - send reset link"""
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('If the email exists, we sent a reset link.', 'info')
            return render_template('forgot_password.html')
        
        # Generate secure token (24h expiry)
        s = URLSafeTimedSerializer(app.secret_key)
        token = s.dumps(user.id, salt='password-reset')
        
        # Store token
        user.reset_token = token
        db.session.commit()
        
        # Mock email (console output)
        reset_url = url_for('reset_password', token=token, _external=True)
        print(f"\n🚀 PASSWORD RESET REQUESTED for {email}")
        print(f"📧 Send this link to user: {reset_url}")
        print(f"⏰ Token expires in 24 hours\n")
        
        flash('Check your email for a password reset link (check console for mock URL)!', 'success')
        return redirect(url_for('login'))
    
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password using token"""
    s = URLSafeTimedSerializer(app.secret_key)
    
    try:
        user_id = s.loads(token, salt='password-reset', max_age=86400)  # 24h
        user = User.query.get(user_id)
    except:
        flash('Invalid or expired token.', 'error')
        return redirect(url_for('login'))
    
    if not user or user.reset_token != token:
        flash('Invalid token.', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('reset_password.html', token=token)
        
        if len(new_password) < 8:
            flash('Password must be at least 8 characters.', 'error')
            return render_template('reset_password.html', token=token)
        
        # Update password and clear token
        user.password = generate_password_hash(new_password)
        user.reset_token = None
        db.session.commit()
        
        flash('Password reset successfully! You can now login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', token=token)

# ==================== PASSENGER ROUTES ====================

@app.route('/passenger/dashboard')
def passenger_dashboard():
    """Passenger dashboard"""
    if session.get('user_role') != 'passenger':
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    bookings = Booking.query.filter_by(user_id=user.id).order_by(Booking.created_at.desc()).all()
    
    return render_template('passenger_dashboard.html', user=user, bookings=bookings)

@app.route('/passenger/book/<int:hotel_id>', methods=['POST'])
def book_hotel(hotel_id):
    """Book a hotel"""
    if session.get('user_role') != 'passenger':
        return redirect(url_for('login'))
    
    hotel = Hotel.query.get_or_404(hotel_id)
    
    check_in = datetime.strptime(request.form.get('check_in'), '%Y-%m-%d').date()
    check_out = datetime.strptime(request.form.get('check_out'), '%Y-%m-%d').date()
    rooms = int(request.form.get('rooms', 1))
    guests = int(request.form.get('guests', 1))
    special_requests = request.form.get('special_requests', '')
    
    # Calculate total price
    nights = (check_out - check_in).days
    total_price = hotel.price * rooms * nights
    
    # Create booking
    booking = Booking(
        user_id=session['user_id'],
        hotel_id=hotel_id,
        check_in=check_in,
        check_out=check_out,
        rooms=rooms,
        guests=guests,
        total_price=total_price,
        status='confirmed',
        special_requests=special_requests
    )
    
    # Update available rooms
    hotel.available_rooms -= rooms
    
    db.session.add(booking)
    db.session.commit()
    
    flash('Booking confirmed successfully!', 'success')
    return redirect(url_for('passenger_dashboard'))

@app.route('/passenger/cancel/<int:booking_id>')
def cancel_booking(booking_id):
    """Cancel a booking"""
    if session.get('user_role') != 'passenger':
        return redirect(url_for('login'))
    
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.user_id != session['user_id']:
        flash('Unauthorized', 'error')
        return redirect(url_for('passenger_dashboard'))
    
    if booking.status in ['cancelled', 'completed']:
        flash('Cannot cancel this booking', 'error')
        return redirect(url_for('passenger_dashboard'))
    
    # Update booking status
    booking.status = 'cancelled'
    
    # Restore available rooms
    hotel = Hotel.query.get(booking.hotel_id)
    hotel.available_rooms += booking.rooms
    
    db.session.commit()
    
    flash('Booking cancelled successfully', 'success')
    return redirect(url_for('passenger_dashboard'))

@app.route('/passenger/review/<int:hotel_id>', methods=['POST'])
def add_review(hotel_id):
    """Add review to a hotel"""
    if session.get('user_role') != 'passenger':
        return redirect(url_for('login'))
    
    rating = int(request.form.get('rating'))
    comment = request.form.get('comment')
    
    review = Review(
        user_id=session['user_id'],
        hotel_id=hotel_id,
        rating=rating,
        comment=comment
    )
    
    # Update hotel rating
    hotel = Hotel.query.get(hotel_id)
    new_review_count = hotel.review_count + 1
    hotel.rating = ((hotel.rating * hotel.review_count) + rating) / new_review_count
    hotel.review_count = new_review_count
    
    db.session.add(review)
    db.session.commit()
    
    flash('Review added successfully', 'success')
    return redirect(url_for('hotel_detail', hotel_id=hotel_id))

@app.route('/passenger/booking-history')
def booking_history():
    """Passenger booking history"""
    if session.get('user_role') != 'passenger':
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    bookings = Booking.query.filter_by(user_id=user.id).order_by(Booking.created_at.desc()).all()
    
    return render_template('passenger_bookings.html', user=user, bookings=bookings)

@app.route('/passenger/favorites')
def favorites():
    """Passenger favorites"""
    if session.get('user_role') != 'passenger':
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    # For now, show all hotels as potential favorites
    # In a full implementation, there would be a favorites table
    hotels = Hotel.query.filter_by(approved=True).limit(6).all()
    
    return render_template('passenger_favorites.html', user=user, hotels=hotels)

@app.route('/passenger/profile')
def profile():
    """Passenger profile"""
    if session.get('user_role') != 'passenger':
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    return render_template('passenger_profile.html', user=user)

@app.route('/passenger/settings')
def settings():
    """Passenger settings"""
    if session.get('user_role') != 'passenger':
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    return render_template('passenger_settings.html', user=user)

@app.route('/passenger/update-profile', methods=['POST'])
def update_profile():
    """Update passenger profile"""
    if session.get('user_role') != 'passenger':
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    user.name = request.form.get('name')
    user.phone = request.form.get('phone')
    
    db.session.commit()
    session['user_name'] = user.name
    
    flash('Profile updated successfully', 'success')
    return redirect(url_for('profile'))

@app.route('/passenger/change-password', methods=['POST'])
def change_password():
    """Change passenger password"""
    if session.get('user_role') != 'passenger':
        return redirect(url_for('login'))
    
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    user = User.query.get(session['user_id'])
    
    if not check_password_hash(user.password, current_password):
        flash('Current password is incorrect', 'error')
        return redirect(url_for('settings'))
    
    if new_password != confirm_password:
        flash('New passwords do not match', 'error')
        return redirect(url_for('settings'))
    
    user.password = generate_password_hash(new_password)
    db.session.commit()
    
    flash('Password changed successfully', 'success')
    return redirect(url_for('settings'))

# ==================== HOTEL OWNER ROUTES ====================

@app.route('/owner/dashboard')
def hotel_owner_dashboard():
    """Hotel owner dashboard"""
    if session.get('user_role') != 'hotel_owner':
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    hotels = Hotel.query.filter_by(owner_id=user.id).all()
    hotel_ids = [h.id for h in hotels]
    
    # Get bookings for owner's hotels
    bookings = Booking.query.filter(Booking.hotel_id.in_(hotel_ids)).order_by(Booking.created_at.desc()).all() if hotel_ids else []
    
    total_revenue = sum(b.total_price for b in bookings if b.status == 'confirmed')
    total_bookings = len(bookings)
    pending_bookings = len([b for b in bookings if b.status == 'pending'])
    
    return render_template('hotel_owner_dashboard.html', 
                         user=user, 
                         hotels=hotels,
                         bookings=bookings,
                         total_revenue=total_revenue,
                         total_bookings=total_bookings,
                         pending_bookings=pending_bookings)

@app.route('/owner/add-hotel', methods=['GET', 'POST'])
def add_hotel():
    """Add new hotel"""
    if session.get('user_role') != 'hotel_owner':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        location = request.form.get('location')
        city = request.form.get('city')
        near_station = request.form.get('near_station')
        near_bus_stop = request.form.get('near_bus_stop')
        price = int(request.form.get('price'))
        total_rooms = int(request.form.get('total_rooms'))
        amenities = request.form.get('amenities')
        
        # Handle photo upload
        photos = []
        if request.files.get('photos'):
            for file in request.files.getlist('photos'):
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    photos.append(filename)
        
        hotel = Hotel(
            name=name,
            description=description,
            location=location,
            city=city,
            near_station=near_station,
            near_bus_stop=near_bus_stop,
            distance_station=round(random.uniform(0.5, 3.0), 1),
            distance_bus=round(random.uniform(0.5, 3.0), 1),
            price=price,
            total_rooms=total_rooms,
            available_rooms=total_rooms,
            amenities=amenities,
            photos=','.join(photos),
            owner_id=session['user_id'],
            approved=False
        )
        
        db.session.add(hotel)
        db.session.commit()
        
        flash('Hotel added successfully! Pending approval from admin.', 'success')
        return redirect(url_for('hotel_owner_dashboard'))
    
    user = User.query.get(session['user_id'])
    return render_template('add_hotel.html', user=user)

@app.route('/owner/manage-booking/<int:booking_id>/<action>')
def manage_booking(booking_id, action):
    """Accept or reject booking"""
    if session.get('user_role') != 'hotel_owner':
        return redirect(url_for('login'))
    
    booking = Booking.query.get_or_404(booking_id)
    hotel = Hotel.query.get(booking.hotel_id)
    
    # Verify owner owns this hotel
    if hotel.owner_id != session['user_id']:
        flash('Unauthorized', 'error')
        return redirect(url_for('hotel_owner_dashboard'))
    
    if action == 'accept':
        booking.status = 'confirmed'
        flash('Booking accepted', 'success')
    elif action == 'reject':
        booking.status = 'cancelled'
        hotel.available_rooms += booking.rooms
        flash('Booking rejected', 'success')
    
    db.session.commit()
    return redirect(url_for('hotel_owner_dashboard'))

@app.route('/owner/my-hotels')
def owner_hotels():
    """View all hotels owned by the user"""
    if session.get('user_role') != 'hotel_owner':
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    hotels = Hotel.query.filter_by(owner_id=user.id).all()
    
    approved_count = len([h for h in hotels if h.approved])
    pending_count = len([h for h in hotels if not h.approved])
    
    # Calculate total revenue
    hotel_ids = [h.id for h in hotels]
    bookings = Booking.query.filter(Booking.hotel_id.in_(hotel_ids)).all() if hotel_ids else []
    total_revenue = sum(b.total_price for b in bookings if b.status == 'confirmed')
    
    return render_template('owner_hotels.html',
                         user=user,
                         hotels=hotels,
                         approved_count=approved_count,
                         pending_count=pending_count,
                         total_revenue=total_revenue)

@app.route('/owner/bookings')
def owner_bookings():
    """View all bookings for owner's hotels"""
    if session.get('user_role') != 'hotel_owner':
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    hotels = Hotel.query.filter_by(owner_id=user.id).all()
    hotel_ids = [h.id for h in hotels]
    
    bookings = Booking.query.filter(Booking.hotel_id.in_(hotel_ids)).order_by(Booking.created_at.desc()).all() if hotel_ids else []
    
    pending_count = len([b for b in bookings if b.status == 'pending'])
    confirmed_count = len([b for b in bookings if b.status == 'confirmed'])
    total_revenue = sum(b.total_price for b in bookings if b.status == 'confirmed')
    
    return render_template('owner_bookings.html',
                         user=user,
                         bookings=bookings,
                         pending_count=pending_count,
                         confirmed_count=confirmed_count,
                         total_revenue=total_revenue)

@app.route('/owner/analytics')
def owner_analytics():
    """View analytics for owner's hotels"""
    if session.get('user_role') != 'hotel_owner':
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    hotels = Hotel.query.filter_by(owner_id=user.id).all()
    hotel_ids = [h.id for h in hotels]
    
    bookings = Booking.query.filter(Booking.hotel_id.in_(hotel_ids)).all() if hotel_ids else []
    
    total_bookings = len(bookings)
    confirmed_bookings = len([b for b in bookings if b.status == 'confirmed'])
    total_revenue = sum(b.total_price for b in bookings if b.status == 'confirmed')
    
    bookings_by_status = {
        'confirmed': len([b for b in bookings if b.status == 'confirmed']),
        'pending': len([b for b in bookings if b.status == 'pending']),
        'completed': len([b for b in bookings if b.status == 'completed']),
        'cancelled': len([b for b in bookings if b.status == 'cancelled']),
    }
    
    # Calculate hotel stats
    hotel_stats = []
    for hotel in hotels:
        hotel_bookings = [b for b in bookings if b.hotel_id == hotel.id]
        hotel_revenue = sum(b.total_price for b in hotel_bookings if b.status == 'confirmed')
        occupancy = 0
        if hotel.total_rooms > 0:
            occupancy = round((hotel.total_rooms - hotel.available_rooms) / hotel.total_rooms * 100, 1)
        
        hotel_stats.append({
            'name': hotel.name,
            'city': hotel.city,
            'booking_count': len(hotel_bookings),
            'revenue': hotel_revenue,
            'rating': hotel.rating,
            'occupancy': occupancy
        })
    
    # Sort by revenue
    hotel_stats = sorted(hotel_stats, key=lambda x: x['revenue'], reverse=True)
    
    avg_booking_value = round(total_revenue / total_bookings, 0) if total_bookings > 0 else 0
    avg_revenue_per_hotel = round(total_revenue / len(hotels), 0) if len(hotels) > 0 else 0
    
    return render_template('owner_analytics.html',
                         user=user,
                         hotels=hotels,
                         total_bookings=total_bookings,
                         confirmed_bookings=confirmed_bookings,
                         total_revenue=total_revenue,
                         bookings_by_status=bookings_by_status,
                         hotel_stats=hotel_stats,
                         avg_booking_value=avg_booking_value,
                         avg_revenue_per_hotel=avg_revenue_per_hotel)

@app.route('/owner/settings')
def owner_settings():
    """Hotel owner settings"""
    if session.get('user_role') != 'hotel_owner':
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    hotels = Hotel.query.filter_by(owner_id=user.id).all()
    hotel_ids = [h.id for h in hotels]
    bookings = Booking.query.filter(Booking.hotel_id.in_(hotel_ids)).all() if hotel_ids else []
    
    return render_template('owner_settings.html',
                         user=user,
                         hotels_count=len(hotels),
                         bookings_count=len(bookings))

@app.route('/owner/update-profile', methods=['POST'])
def owner_update_profile():
    """Update hotel owner profile"""
    if session.get('user_role') != 'hotel_owner':
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    user.name = request.form.get('name')
    user.phone = request.form.get('phone')
    
    db.session.commit()
    session['user_name'] = user.name
    
    flash('Profile updated successfully', 'success')
    return redirect(url_for('owner_settings'))

@app.route('/owner/change-password', methods=['POST'])
def owner_change_password():
    """Change hotel owner password"""
    if session.get('user_role') != 'hotel_owner':
        return redirect(url_for('login'))
    
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    user = User.query.get(session['user_id'])
    
    if not check_password_hash(user.password, current_password):
        flash('Current password is incorrect', 'error')
        return redirect(url_for('owner_settings'))
    
    if new_password != confirm_password:
        flash('New passwords do not match', 'error')
        return redirect(url_for('owner_settings'))
    
    user.password = generate_password_hash(new_password)
    db.session.commit()
    
    flash('Password changed successfully', 'success')
    return redirect(url_for('owner_settings'))

# ==================== ADMIN ROUTES ====================

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard"""
    if session.get('user_role') != 'admin':
        return redirect(url_for('login'))
    
    # Get current user
    user = User.query.get(session['user_id'])
    
    # Get statistics
    total_users = User.query.count()
    total_hotels = Hotel.query.count()
    approved_hotels = Hotel.query.filter_by(approved=True).count()
    pending_hotels = Hotel.query.filter_by(approved=False).count()
    total_bookings = Booking.query.count()
    total_revenue = db.session.query(db.func.sum(Booking.total_price)).filter(Booking.status == 'confirmed').scalar() or 0
    
    # Recent bookings
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(10).all()
    
    # Users by role
    passengers = User.query.filter_by(role='passenger').count()
    hotel_owners = User.query.filter_by(role='hotel_owner').count()
    
    return render_template('admin_dashboard.html',
                         user=user,
                         total_users=total_users,
                         total_hotels=total_hotels,
                         approved_hotels=approved_hotels,
                         pending_hotels=pending_hotels,
                         total_bookings=total_bookings,
                         total_revenue=total_revenue,
                         recent_bookings=recent_bookings,
                         passengers=passengers,
                         hotel_owners=hotel_owners)

@app.route('/admin/users')
def manage_users():
    """Manage users"""
    if session.get('user_role') != 'admin':
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin_users.html', users=users, user=user)

@app.route('/admin/hotels')
def manage_hotels():
    """Manage hotel listings"""
    if session.get('user_role') != 'admin':
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    pending_hotels = Hotel.query.filter_by(approved=False).all()
    approved_hotels = Hotel.query.filter_by(approved=True).all()
    
    return render_template('admin_hotels.html', 
                         pending_hotels=pending_hotels,
                         approved_hotels=approved_hotels,
                         user=user)

@app.route('/admin/approve-hotel/<int:hotel_id>')
def approve_hotel(hotel_id):
    """Approve a hotel"""
    if session.get('user_role') != 'admin':
        return redirect(url_for('login'))
    
    hotel = Hotel.query.get_or_404(hotel_id)
    hotel.approved = True
    db.session.commit()
    
    flash('Hotel approved successfully', 'success')
    return redirect(url_for('manage_hotels'))

@app.route('/admin/reject-hotel/<int:hotel_id>')
def reject_hotel(hotel_id):
    """Reject a hotel"""
    if session.get('user_role') != 'admin':
        return redirect(url_for('login'))
    
    hotel = Hotel.query.get_or_404(hotel_id)
    db.session.delete(hotel)
    db.session.commit()
    
    flash('Hotel rejected and removed', 'success')
    return redirect(url_for('manage_hotels'))

@app.route('/admin/bookings')
def manage_bookings():
    """View all bookings"""
    if session.get('user_role') != 'admin':
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    return render_template('admin_bookings.html', bookings=bookings, user=user)

@app.route('/admin/analytics')
def analytics():
    """Admin analytics"""
    if session.get('user_role') != 'admin':
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    # Get statistics
    total_users = User.query.count()
    total_hotels = Hotel.query.filter_by(approved=True).count()
    total_bookings = Booking.query.count()
    total_revenue = db.session.query(db.func.sum(Booking.total_price)).filter(Booking.status == 'confirmed').scalar() or 0
    
    # Bookings by month (sample data)
    bookings_by_status = {
        'confirmed': Booking.query.filter_by(status='confirmed').count(),
        'pending': Booking.query.filter_by(status='pending').count(),
        'completed': Booking.query.filter_by(status='completed').count(),
        'cancelled': Booking.query.filter_by(status='cancelled').count(),
    }
    
    # Top cities
    top_cities = db.session.query(Hotel.city, db.func.count(Hotel.id)).group_by(Hotel.city).limit(5).all()
    
    return render_template('admin_analytics.html', 
                         user=user,
                         total_users=total_users,
                         total_hotels=total_hotels,
                         total_bookings=total_bookings,
                         total_revenue=total_revenue,
                         bookings_by_status=bookings_by_status,
                         top_cities=top_cities)

@app.route('/admin/settings', methods=['GET', 'POST'])
def admin_settings():
    """Admin settings"""
    if session.get('user_role') != 'admin':
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_profile':
            user.name = request.form.get('name')
            user.phone = request.form.get('phone')
            db.session.commit()
            flash('Profile updated successfully', 'success')
        elif action == 'change_password':
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if not check_password_hash(user.password, current_password):
                flash('Current password is incorrect', 'error')
            elif new_password != confirm_password:
                flash('New passwords do not match', 'error')
            else:
                user.password = generate_password_hash(new_password)
                db.session.commit()
                flash('Password changed successfully', 'success')
        
        return redirect(url_for('admin_settings'))
    
    return render_template('admin_settings.html', user=user)

@app.route('/admin/ads')
def admin_ads():
    """Admin advertisements"""
    if session.get('user_role') != 'admin':
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    ads = Advertisement.query.order_by(Advertisement.created_at.desc()).all()
    
    # Calculate stats
    total_impressions = sum(ad.impressions for ad in ads)
    total_clicks = sum(ad.clicks for ad in ads)
    total_spent = sum(ad.budget for ad in ads)
    click_rate = round((total_clicks / total_impressions * 100) if total_impressions > 0 else 0, 2)
    
    return render_template('admin_ads.html',
                         user=user,
                         ads=ads,
                         total_impressions=total_impressions,
                         total_clicks=total_clicks,
                         total_spent=total_spent,
                         click_rate=click_rate)

@app.route('/admin/create-ad', methods=['POST'])
def create_ad():
    """Create new advertisement"""
    if session.get('user_role') != 'admin':
        return redirect(url_for('login'))
    
    title = request.form.get('title')
    content = request.form.get('content')
    position = request.form.get('position')
    link = request.form.get('link')
    budget = int(request.form.get('budget', 0))
    
    ad = Advertisement(
        title=title,
        content=content,
        position=position,
        link=link,
        budget=budget,
        status='active'
    )
    
    db.session.add(ad)
    db.session.commit()
    
    flash('Advertisement created successfully', 'success')
    return redirect(url_for('admin_ads'))

@app.route('/admin/edit-ad/<int:ad_id>', methods=['GET', 'POST'])
def edit_ad(ad_id):
    """Edit advertisement"""
    if session.get('user_role') != 'admin':
        return redirect(url_for('login'))
    
    ad = Advertisement.query.get_or_404(ad_id)
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        ad.title = request.form.get('title')
        ad.content = request.form.get('content')
        ad.position = request.form.get('position')
        ad.link = request.form.get('link')
        ad.budget = int(request.form.get('budget', 0))
        ad.status = request.form.get('status')
        
        db.session.commit()
        flash('Advertisement updated successfully', 'success')
        return redirect(url_for('admin_ads'))
    
    return render_template('admin_edit_ad.html', ad=ad, user=user)

@app.route('/admin/delete-ad/<int:ad_id>')
def delete_ad(ad_id):
    """Delete advertisement"""
    if session.get('user_role') != 'admin':
        return redirect(url_for('login'))
    
    ad = Advertisement.query.get_or_404(ad_id)
    db.session.delete(ad)
    db.session.commit()
    
    flash('Advertisement deleted successfully', 'success')
    return redirect(url_for('admin_ads'))

# ==================== API ROUTES ====================

@app.route('/api/hotels')
def api_hotels():
    """API to get hotels with filters"""
    city = request.args.get('city')
    min_price = request.args.get('min_price', type=int)
    max_price = request.args.get('max_price', type=int)
    min_rating = request.args.get('min_rating', type=float)
    
    query = Hotel.query.filter_by(approved=True)
    
    if city:
        query = query.filter(Hotel.city.ilike(f'%{city}%'))
    if min_price:
        query = query.filter(Hotel.price >= min_price)
    if max_price:
        query = query.filter(Hotel.price <= max_price)
    if min_rating:
        query = query.filter(Hotel.rating >= min_rating)
    
    hotels = query.all()
    
    return jsonify([{
        'id': h.id,
        'name': h.name,
        'city': h.city,
        'location': h.location,
        'near_station': h.near_station,
        'near_bus_stop': h.near_bus_stop,
        'price': h.price,
        'rating': h.rating,
        'distance_station': h.distance_station,
        'distance_bus': h.distance_bus
    } for h in hotels])

# ==================== DATABASE SETUP ====================

def init_db():
    """Initialize database with tables and sample data"""
    with app.app_context():
        db.create_all()
        
        # Check if data already exists
        if User.query.first():
            print("Database already has data!")
            return
        
        # Create Admin
        admin = User(
            name='Admin',
            email='admin@railbusatithi.com',
            password=generate_password_hash('admin123'),
            role='admin',
            phone='9999999999'
        )
        db.session.add(admin)
        
        # Create Hotel Owners
        owner1 = User(
            name='Rahul Sharma',
            email='rahul@hotel.com',
            password=generate_password_hash('owner123'),
            role='hotel_owner',
            phone='9876543210',
            city='Mumbai',
            location='Near CST Station, Mumbai'
        )
        owner2 = User(
            name='Priya Patel',
            email='priya@hotel.com',
            password=generate_password_hash('owner123'),
            role='hotel_owner',
            phone='9876543211',
            city='Delhi',
            location='Near New Delhi Railway Station'
        )
        db.session.add(owner1)
        db.session.add(owner2)
        
        # Create Passengers
        passengers_data = [
            ('Amit Kumar', 'amit@email.com', '9876543201'),
            ('Sneha Gupta', 'sneha@email.com', '9876543202'),
            ('Raj Malhotra', 'raj@email.com', '9876543203'),
            ('Anjali Singh', 'anjali@email.com', '9876543204'),
            ('Vikram Joshi', 'vikram@email.com', '9876543205'),
        ]
        
        passengers = []
        for name, email, phone in passengers_data:
            p = User(
                name=name,
                email=email,
                password=generate_password_hash('passenger123'),
                role='passenger',
                phone=phone
            )
            passengers.append(p)
            db.session.add(p)
        
        db.session.commit()
        
        # Create Hotels
        hotels_data = [
            ('Grand Hotel Mumbai', 'Mumbai', 'Near CST Station', 'Dadar Bus Stand', 2500, 4.5),
            ('Railway View Inn', 'Delhi', 'Near New Delhi Railway Station', 'ISBT Delhi', 1800, 4.2),
            ('Bus Stand Residency', 'Bangalore', 'Yeshwantpur Railway Station', 'Majestic Bus Stand', 2200, 4.3),
            ('Station Square Hotel', 'Chennai', 'Central Railway Station', 'CMBT Bus Terminal', 2000, 4.1),
            ('Travelers Paradise', 'Kolkata', 'Howrah Railway Station', 'Esplanade Bus Stand', 1900, 4.4),
            ('Express Stay', 'Hyderabad', 'Secunderabad Railway Station', 'Jubilee Bus Stand', 2100, 4.0),
            ('Bus Route Hotel', 'Pune', 'Pune Railway Station', 'Shivaji Nagar Bus Stand', 1700, 4.3),
            ('Station Hotel Jaipur', 'Jaipur', 'Jaipur Railway Station', 'Sindhi Camp Bus Stand', 1600, 4.6),
            ('Transit Inn', 'Mumbai', 'Bandra Railway Station', 'Bandra Bus Stand', 3000, 4.7),
            ('Journey Lodge', 'Delhi', 'Old Delhi Railway Station', 'Kashmere Gate ISBT', 2100, 4.2),
        ]
        
        hotels = []
        for name, city, station, bus, price, rating in hotels_data:
            h = Hotel(
                name=name,
                description=f'Comfortable stay near {station} and {bus}',
                location=f'Near {station}',
                city=city,
                near_station=station,
                near_bus_stop=bus,
                distance_station=round(random.uniform(0.5, 2.5), 1),
                distance_bus=round(random.uniform(0.5, 2.5), 1),
                price=price,
                rating=rating,
                review_count=random.randint(10, 100),
                total_rooms=random.randint(10, 30),
                available_rooms=random.randint(5, 20),
                amenities='WiFi,AC,Parking,Room Service,Restaurant,Laundry',
                owner_id=random.choice([owner1.id, owner2.id]),
                approved=True
            )
            hotels.append(h)
            db.session.add(h)
        
        db.session.commit()
        
        # Create Bookings
        statuses = ['confirmed', 'completed', 'pending']
        for _ in range(15):
            hotel = random.choice(hotels)
            user = random.choice(passengers)
            
            check_in = datetime.now().date()
            check_out = check_in + timedelta(days=random.randint(1, 5))
            
            booking = Booking(
                user_id=user.id,
                hotel_id=hotel.id,
                check_in=check_in,
                check_out=check_out,
                rooms=random.randint(1, 2),
                guests=random.randint(1, 3),
                total_price=hotel.price * random.randint(1, 2) * random.randint(1, 5),
                status=random.choice(statuses)
            )
            db.session.add(booking)
        
        db.session.commit()
        
        print("Database initialized with sample data!")

# ==================== MAIN ====================

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5102, host='0.0.0.0')

