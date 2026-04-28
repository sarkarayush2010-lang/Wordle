from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask import Flask, render_template, request, redirect, flash, session
from datetime import datetime
from bson.objectid import ObjectId 
from passlib.hash import sha256_crypt

app = Flask('manager')
app.secret_key="key"
uri = "mongodb+srv://sarkarayush2010_db_user:M0ljRqIDayb5O0AS@note-project.njve7ym.mongodb.net/?appName=Note-Project"

client = MongoClient(uri, server_api=ServerApi('1'))
db = client['Note-Project'] 
shop_collection = db['shopitems']
accounts_collection = db['accounts']

@app.route('/')
def index():
    all_products = list(shop_collection.find())
    all_stores = list(accounts_collection.find())
    
    return render_template('shop.html', products=all_products, stores=all_stores)

@app.route('/shophome')
def shophome():
    email = session.get('user_email')
    if not email:
        return redirect('/')
    
    products = list(shop_collection.find({"owner_email": email}))
    return render_template('shophome.html', products=products)

@app.route('/register', methods=['POST'])
def register():
    shop_name = request.form.get('shop_name')
    owner_name = request.form.get('owner_name')
    email = request.form.get('email')
    contact = request.form.get('contact')
    password = sha256_crypt.hash(request.form.get('password'))

    new_user = {
        "shop_name": shop_name,
        "owner_name": owner_name,
        "email": email,
        "contact": contact,
        "password": password,
        "created_at": datetime.now()
    }
    accounts_collection.insert_one(new_user)
    flash("Sign up successful")
    return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password_attempt = request.form.get('password')
    user = accounts_collection.find_one({"email": email})
    
    if user and sha256_crypt.verify(password_attempt, user['password']):
        session['user_email'] = email
        flash("Log in successful")
        return redirect('/shophome')
    else:
        flash("Invalid email or password")
        return redirect('/')

@app.route('/add_product', methods=['POST'])
def add_product():
    new_item = {
        "name": request.form.get('name'),
        "description": request.form.get('description'),
        "price": request.form.get('price'),
        "quantity": int(request.form.get('quantity')),
        "image_link": request.form.get('image_link'),
        "owner_email": request.form.get('owner_email'), 
        "created_at": datetime.now()
    }
    shop_collection.insert_one(new_item)
    flash("Product added successfully")
    return redirect('/shophome')

@app.route('/add_stock/<product_id>', methods=['POST'])
def add_stock(product_id):
    added_qty = int(request.form.get('added_quantity'))
    shop_collection.update_one(
        {"_id": ObjectId(product_id)},
        {"$inc": {"quantity": added_qty}}
    )
    flash("Stock updated")
    return redirect('/shophome')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)