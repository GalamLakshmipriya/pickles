from flask import Flask, render_template, request, redirect, url_for, session, flash
import boto3
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# AWS Configuration
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
user_table = dynamodb.Table('Users')
orders_table = dynamodb.Table('Orders')

# Email Configuration
EMAIL_ADDRESS = 'laharikessamsetty@gmail.com'
EMAIL_PASSWORD = 'iyxh zneg oyog tyui' # Replace with your actual Gmail App Password

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize database
def init_db():
    if not os.path.exists('users.db'):
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

init_db()

# Sample product data
veg_pickles = [
    {'name': 'Tomato Pickle', 'price': 150, 'image': 'static/images/tomato.jpg'},
    {'name': 'Mango Pickle', 'price': 130, 'image': 'static/images/mango.jpg'},
    {'name': 'Lemon Pickle', 'price': 120, 'image': 'static/images/lemon.jpg'}
]

non_veg_pickles = [
    {'name': 'Chicken Pickle', 'price': 250, 'image': 'static/images/chicken.jpg'},
    {'name': 'Mutton Pickle', 'price': 300, 'image': 'static/images/mutton.jpg'}
]

snacks = [
    {'name': 'Mixture', 'price': 60, 'image': 'static/images/mixture.jpg'},
    {'name': 'Murukku', 'price': 50, 'image': 'static/images/murukku.jpg'}
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/veg_pickles')
def veg_pickles_page():
    return render_template('veg_pickles.html', items=veg_pickles)

@app.route('/non_veg_pickles')
def non_veg_pickles_page():
    return render_template('non_veg_pickles.html', items=non_veg_pickles)

@app.route('/snacks')
def snacks_page():
    return render_template('snacks.html', items=snacks)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contactus')
def contactus():
    return render_template('contactus.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['user'] = email
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
            conn.commit()
            flash('Signup successful. Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already registered.', 'danger')
            return redirect(url_for('signup'))
        finally:
            conn.close()
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/cart')
def cart():
    if 'cart' not in session:
        session['cart'] = []
    total = sum(item['price'] * item['quantity'] for item in session['cart'])
    return render_template('cart.html', cart=session['cart'], total=total)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    item_name = request.form.get('item_name')
    price = float(request.form.get('price'))
    image = request.form.get('image')
    quantity = int(request.form.get('quantity'))

    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append({
        'item': item_name,
        'price': price,
        'image': image,
        'quantity': quantity
    })
    session.modified = True
    return redirect(url_for('cart'))

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    index = request.form.get('index')
    if index is not None:
        index = int(index)
        if 'cart' in session and 0 <= index < len(session['cart']):
            session['cart'].pop(index)
            session.modified = True
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'cart' not in session or not session['cart']:
        flash('Your cart is empty. Add items before checkout.', 'warning')
        return redirect(url_for('cart'))

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        # Order saving logic can go here

        session.pop('cart', None)
        flash('Order placed successfully!', 'success')
        return redirect(url_for('success'))

    return render_template('checkout.html')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').strip().lower()
    results = []

    for item in veg_pickles + non_veg_pickles + snacks:
        if query in item['name'].lower():
            results.append(item)

    return render_template('search_results.html', query=query, results=results)

    # Email Sending Function
def send_email(to_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")

if name == '__main__':
 app.run(debug=True, host='0.0.0.0', port=5000)