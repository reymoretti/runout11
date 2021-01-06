import os
import random
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort, session
from app import app, db, bcrypt, mail
from app.forms import (RegistrationFormCustomer, RegistrationFormFoodseller, LoginForm,
                       UpdateCustomerAccountForm, UpdateFoodsellerAccountForm, OfferForm, ReviewForm,
                       SearchForm, RequestResetForm, ResetPasswordForm)
from app.models import Customer, Foodseller, Offer, OfferInShoppingList, Review
from flask_login import login_user, current_user, logout_user, login_required
from app import send_email
from flask_mail import Message

@app.route('/')
@app.route('/about')
def about():
    customers = Customer.query.count()
    offers = Offer.query.count()
    foodsellers = Foodseller.query.count()
    return render_template('about.html', title='About Us', customers=customers, offers=offers, foodsellers=foodsellers)

@app.route('/registerFoodseller',methods=['GET','POST'])
def registerFoodseller():
    if current_user.is_authenticated:
        return redirect(url_for('about'))
    form = RegistrationFormFoodseller()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data.decode('utf-8'))
        register = Foodseller(foodsellerName=form.foodsellerName.data,
                              email=form.email.data,
                              city=form.city.data.upper(),
                              address=form.address.data,
                              phone_number=form.phone_number.data,
                              opening_hours=form.opening_hours.data,
                              password=hashed_password)
        db.session.add(register)
        db.session.commit()
        flash('Account created for %s, you can login now' % form.foodsellerName.data)
        send_email(form.email.data,
                   'Registration completed successfully',
                   'email',
                   username=form.foodsellerName.data)
        return redirect(url_for('login'))
    return render_template('registerFoodseller.html', title='Register', form=form)

@app.route('/registerCustomer',methods=['GET','POST'])
def registerCustomer():
    if current_user.is_authenticated:
        return redirect(url_for('customerPage'))
    form = RegistrationFormCustomer()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data.decode('utf-8'))
        register = Customer(username=form.username.data,
                            name=form.name.data,
                            surname=form.surname.data,
                            email=form.email.data,
                            city=form.city.data.upper(),
                            password=hashed_password)
        db.session.add(register)
        db.session.commit()
        flash('Account created for %s, you can login now' % form.username.data)
        send_email(form.email.data,
                   'Registration completed successfully',
                   'email',
                   username=form.username.data)
        return redirect(url_for('login'))
    return render_template('registerCustomer.html', title='Register', form=form)

@app.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        if session['type'] == 'customer':
            return redirect(url_for('customerPage'))
        else:
            return redirect(url_for('foodsellerPage'))

    form = LoginForm()
    if form.validate_on_submit():
        user = Customer.query.filter_by(email=form.email.data).first()
        session['type'] = 'customer'
        if user is None:
            user = Foodseller.query.filter_by(email=form.email.data).first()
            session['type'] = 'foodseller'
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            if session['type'] == 'foodseller':
                return redirect(url_for('foodsellerPage'))
            else:
                return redirect(url_for('customerPage'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('about'))

def save_picture(form_picture):
    random_number = random.randint(0, 16777215)
    hex_number = str(hex(random_number))
    hex_number = '#' + hex_number[2:]
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = hex_number + f_ext
    picture_path = os.path.join(app.root_path, 'static/pictures', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route('/customerAccount',methods=['GET','POST'])
@login_required
def customerAccount():
    form = UpdateCustomerAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.name = form.name.data
        current_user.surname = form.surname.data
        current_user.city = form.city.data.upper()
        db.session.commit()
        flash('Account updated')
        return redirect(url_for('customerAccount'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.name.data = current_user.name
        form.surname.data = current_user.surname
        form.city.data = current_user.city
    image_file = url_for('static', filename='pictures/' + current_user.image_file)
    return render_template('customerAccount.html', title='Account',
                           image_file=image_file, form=form)

@app.route('/foodsellerAccount',methods=['GET','POST'])
@login_required
def foodsellerAccount():
    form = UpdateFoodsellerAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.foodsellerName = form.foodsellerName.data
        current_user.email = form.email.data
        current_user.city = form.city.data.upper()
        current_user.address = form.address.data
        current_user.phone_number = form.phone_number.data
        current_user.opening_hours = form.opening_hours.data
        db.session.commit()
        flash('Account updated')
        return redirect(url_for('foodsellerAccount'))
    elif request.method == 'GET':
        form.foodsellerName.data = current_user.foodsellerName
        form.email.data = current_user.email
        form.city.data = current_user.city
        form.address.data = current_user.address
        form.phone_number.data = current_user.phone_number
        form.opening_hours.data = current_user.opening_hours
    image_file = url_for('static', filename='pictures/' + current_user.image_file)
    return render_template('foodsellerAccount.html', title='Account',
                           image_file=image_file, form=form)

@app.route('/customerPage')
def customerPage():
    if session['type'] == "foodseller":
        return redirect(url_for('foodsellerPage'))
    elif session['type'] == "customer":
        offers = Offer.query.all()
        selected_offers = OfferInShoppingList.query.filter_by(customer_id=current_user.id)
        selected_offers_id = [x.offer_id for x in selected_offers] #we create a list of id of selected items
        return render_template('customerPage.html', offers=offers,
                               selected_offers_id=selected_offers_id)
    else:
        return redirect(url_for('login'))

@app.route('/foodsellerPage')
def foodsellerPage():
    if session['type'] == "customer":
        return redirect(url_for('customerPage'))
    elif session['type'] == "foodseller":
        offers = Offer.query.all()
        return render_template('foodsellerPage.html', offers=offers)
    else:
        return redirect(url_for('login'))

@app.route('/offer/new', methods=['GET','POST'])
@login_required
def new_offer():
    form = OfferForm()
    if form.validate_on_submit():
        offer = Offer(offer_name=form.offer_name.data, brand=form.brand.data,
                      description=form.description.data, exp_date=form.exp_date.data,
                      price=form.price.data, percentage_discount=form.percentage_discount.data,
                      seller=current_user)
        db.session.add(offer)
        db.session.commit()
        flash('Offer created!')
        return redirect(url_for('foodsellerPage'))
    return render_template('create_offer.html', title='New Offer', form=form, legend='New Offer')

@app.route('/offer/<int:offer_id>')
def offer(offer_id):
    offer = Offer.query.get_or_404(offer_id)
    return render_template('offer.html', offer_name=offer.offer_name, offer=offer)

@app.route('/offer/<int:offer_id>/update',methods=['GET','POST'])
def update_offer(offer_id):
    offer = Offer.query.get_or_404(offer_id)
    form = OfferForm()
    if form.validate_on_submit():
        offer.offer_name = form.offer_name.data
        offer.brand = form.brand.data
        offer.description = form.description.data
        offer.exp_date = form.exp_date.data
        offer.price = form.price.data
        offer.percentage_discount = form.percentage_discount.data
        db.session.commit()
        flash('Offer updated!')
        return redirect(url_for('offer', offer_id=offer.id))
    elif request.method == 'GET':
        form.offer_name.data = offer.offer_name
        form.brand.data = offer.brand
        form.description.data = offer.description
        form.exp_date.data = offer.exp_date
        form.price.data = offer.price
        form.percentage_discount.data = offer.percentage_discount
    return render_template('create_offer.html', title='Update Offer',
                           form=form, legend='Update Offer')

@app.route('/offer/<int:offer_id>/delete',methods=['POST'])
def delete_offer(offer_id):
    offer = Offer.query.get_or_404(offer_id)
    db.session.delete(offer)
    db.session.commit()
    flash('Offer deleted!')
    return redirect(url_for('foodsellerPage'))

@app.route("/foodseller/<string:foodsellerName>")
def foodseller_offers(foodsellerName):
    foodseller = Foodseller.query.filter_by(foodsellerName=foodsellerName).first_or_404()
    offers = Offer.query.filter_by(seller=foodseller)
    offers_number = Offer.query.count()
    return render_template('foodsellerOffers.html', foodseller=foodseller,
                           offers=offers, offers_number=offers_number)

@app.route("/myShoppingList/<int:offer_id>", methods=['GET','POST','DELETE'])
def my_shopping_list(offer_id):
    selected_offer = OfferInShoppingList(offer_id=offer_id, customer_id=current_user.id)
    db.session.add(selected_offer)
    db.session.commit()
    return redirect(url_for('customerPage'))

@app.route("/myShoppingList")
def shoplist():
    selected_offers = OfferInShoppingList.query.filter_by(customer_id=current_user.id)
    selected_offers_number = OfferInShoppingList.query.filter_by(customer_id=current_user.id).count()
    offer = Offer.query.all()
    return render_template('ShoppingList.html', selected_offers=selected_offers,
                           offer=offer, selected_offers_number=selected_offers_number)

@app.route('/myShoppingList/<int:offer_id>/delete',methods=['GET','POST','DELETE'])
def remove_from_shoplist(offer_id):
    offer = OfferInShoppingList.query.filter_by(offer_id=offer_id, customer_id=current_user.id).first()
    db.session.delete(offer)
    db.session.commit()
    flash('Offer removed from shopping list!')
    return redirect(url_for('shoplist'))


def send_reset_email_customer(customer):
    token = customer.get_reset_token()
    msg = Message('Password Reset Request', sender='runoutweb@gmail.com', recipients=[customer.email])
    msg.body = 'To reset your password, visit the following link: %s ' \
               'If you did not make this request then simply ignore this email and no changes will be made' \
               %({url_for('reset_token', token=token, _external=True)})
    mail.send(msg)

def send_reset_email_foodseller(foodseller):
    token = foodseller.get_reset_token()
    msg = Message('Password Reset Request', sender='runoutweb@gmail.com', recipients=[foodseller.email])
    msg.body = 'To reset your password, visit the following link: %s ' \
               'If you did not make this request then simply ignore this email and no changes will be made' \
               %({url_for('reset_token', token=token, _external=True)})
    mail.send(msg)

@app.route("/reset_password", methods=['GET','POST']) #route where the user asks to reset password
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        customer = Customer.query.filter_by(email=form.email.data).first()
        if customer is None:
            foodseller = Foodseller.query.filter_by(email=form.email.data).first()
            send_reset_email_foodseller(foodseller)
            flash('An email has been sent to reset your password')
            return redirect(url_for('login'))
        else:
            send_reset_email_customer(customer)
            flash('An email has been sent to reset your password')
            return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route("/reset_password/<token>", methods=['GET','POST']) #route where the user resets password
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    customer = Customer.verify_reset_token(token)
    if customer is None:
        foodseller = Foodseller.verify_reset_token(token)
        if foodseller is None:
            flash('that is an invalid or expired token')
            return redirect(url_for('reset_request'))
        else:
            form = ResetPasswordForm()
            if form.validate_on_submit():
                hashed_password = bcrypt.generate_password_hash(form.password.data.decode('utf-8'))
                foodseller.password = hashed_password
                db.session.commit()
                flash('Password updated, you can login now')
                return redirect(url_for('login'))
    else:
        form = ResetPasswordForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data.decode('utf-8'))
            customer.password = hashed_password
            db.session.commit()
            flash('Password updated, you can login now')
            return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

@app.route("/review/<int:foodseller_id>", methods=['GET','POST','DELETE'])
def new_review(foodseller_id):
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(vote=form.vote.data, text=form.text.data,
                        customer_id=current_user.id, foodseller_id=foodseller_id)
        db.session.add(review)
        db.session.commit()
        foodsellerName=review.foodseller.foodsellerName
        flash('Review created!')
        return redirect(url_for('foodseller_reviews', foodsellerName=foodsellerName))
    return render_template('create_review.html', title='New Review', form=form, legend='New Review')

@app.route("/foodseller_reviews/<string:foodsellerName>", methods=['GET','POST'])
def foodseller_reviews(foodsellerName):
    foodseller = Foodseller.query.filter_by(foodsellerName=foodsellerName).first_or_404()
    reviews = Review.query.filter_by(foodseller_id=foodseller.id)
    return render_template('reviews.html', reviews=reviews, foodseller=foodseller, title='Reviews', legend='All Reviews')

@app.route('/review/<int:review_id>/delete',methods=['POST'])
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    foodsellerName = review.foodseller.foodsellerName
    db.session.delete(review)
    db.session.commit()
    flash('Review deleted!')
    return redirect(url_for('foodseller_reviews', foodsellerName=foodsellerName))

@app.route("/search_request", methods=['GET','POST'])
def search_request():
    form = SearchForm()
    if form.validate_on_submit():
        offers = Offer.query.filter_by(offer_name=form.offer_name.data)
        offs = []
        for offer in offers:
            offs.append(offer.offer_name)
        comma_separated = ','.join(offs) #we create a string from the list of the names of the offers
                                         #to be able to send them to the next route
        return redirect(url_for('search_results', offers=comma_separated))
    return render_template('searchRequest.html', form=form)

@app.route("/search_results/<string:offers>", methods=['GET','POST'])
def search_results(offers):
    offers = offers.split(',') #it is a string, so we need to create a list of offers (objects)
    all_offers = Offer.query.all()
    offer_objects = []
    l1 = []
    for offer in all_offers:
        for off in offers:
            if offer.offer_name.lower() == off.lower():
                offer_objects.append(offer)
    selected_offers = OfferInShoppingList.query.filter_by(customer_id=current_user.id)
    selected_offers_id = [x.offer_id for x in selected_offers]  # we create a list of id of selected items
    return render_template('search.html', offers=offer_objects, selected_offers_id=selected_offers_id,
                           title='Search', legend='Search results')


@app.errorhandler(404)
def invalid_route(e):
    flash('There is no offers matching your search terms')
    return redirect(url_for('search_request'))


