#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'

@app.route('/bakeries')
def get_bakeries():
    bakeries = [bakery.to_dict() for bakery in Bakery.query.all()]
    return make_response(bakeries, 200)

@app.route('/bakeries/<int:id>')
def get_bakery(id):
    bakery = db.session.query(Bakery).get(id)
    if not bakery:
        return make_response({'error': 'Bakery not found'}, 404)
    return make_response(bakery.to_dict(), 200)

@app.route('/bakeries/<int:id>', methods=['PATCH'])
def update_bakery(id):
    bakery = db.session.query(Bakery).get(id)
    if not bakery:
        return make_response({'error': 'Bakery not found'}, 404)

    # Receive form data
    name = request.form.get('name')
    if name:
        bakery.name = name

    db.session.commit()
    return make_response(bakery.to_dict(), 200)

@app.route('/baked_goods/by_price')
def baked_goods_by_price():
    goods = BakedGood.query.order_by(BakedGood.price.desc()).all()
    return make_response([g.to_dict() for g in goods], 200)

@app.route('/baked_goods/most_expensive')
def most_expensive_baked_good():
    good = BakedGood.query.order_by(BakedGood.price.desc()).first()
    return make_response(good.to_dict(), 200)

@app.route('/baked_goods', methods=['POST'])
def create_baked_good():
    # Receive form data
    name = request.form.get('name')
    price = request.form.get('price')
    bakery_id = request.form.get('bakery_id')

    if not all([name, price, bakery_id]):
        return make_response({'error': 'Missing required fields'}, 400)

    try:
        price = float(price)
        bakery_id = int(bakery_id)
    except ValueError:
        return make_response({'error': 'Invalid price or bakery_id'}, 400)

    new_good = BakedGood(name=name, price=price, bakery_id=bakery_id)
    db.session.add(new_good)
    db.session.commit()

    return make_response(new_good.to_dict(), 201)

@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    baked_good = BakedGood.query.get(id)
    if not baked_good:
        return make_response({'error': 'Baked good not found'}, 404)

    db.session.delete(baked_good)
    db.session.commit()
    return make_response({'message': 'Baked good deleted successfully'}, 200)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
