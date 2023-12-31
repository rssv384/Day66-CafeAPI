from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy()
db.init_app(app)


# API Key for HTTP DELETE authentication
SECRET_API_KEY = 'TopSecretApiKey'


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self) -> dict:
        """Returns the object as a dictionary.

        Returns:
            dict: Object as a dictionary.
        """
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}

# COMMENT OUT AFTER FIRST RUN
# with app.app_context():
#     db.create_all()


@app.route('/')
def home():
    return render_template('index.html')


# HTTP GET - Read Record
@app.route('/random')
def get_random_cafe():
    random_cafe = db.session.scalars(
        db.select(Cafe).order_by(db.func.random())).first()
    return jsonify(cafe=random_cafe.to_dict())


@app.route('/all')
def get_all_cafes():
    results = db.session.execute(db.select(Cafe).order_by(Cafe.name))
    all_cafes = [cafe.to_dict() for cafe in results.scalars().all()]
    return jsonify(cafes=all_cafes)


@app.route('/search')
def get_cafe_at_location():
    query_location = request.args.get('loc')
    results = db.session.execute(db.select(Cafe).where(
        Cafe.location == query_location))
    all_cafes = [cafe.to_dict() for cafe in results.scalars().all()]
    if all_cafes:
        return jsonify(cafes=all_cafes)
    else:
        return jsonify(error={'Not Found': 'Sorry, we could not find a cafe in that location.'})


# HTTP POST - Create Record
@app.route('/add', methods=['POST'])
def post_new_cafe():
    new_cafe = Cafe(
        name=request.form.get('name'),
        map_url=request.form.get('map_url'),
        img_url=request.form.get('img_url'),
        location=request.form.get('loc'),
        seats=request.form.get('seats'),
        has_toilet=bool(request.form.get('has_toilet')),
        has_wifi=bool(request.form.get('has_wifi')),
        has_sockets=bool(request.form.get('has_sockets')),
        can_take_calls=bool(request.form.get('calls')),
        coffee_price=request.form.get('coffee_price')
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={'success': 'Successfully added the new cafe.'})


# HTTP PUT/PATCH - Update Record
@app.route('/update_price/<int:cafe_id>', methods=['PATCH'])
def update_coffee_price(cafe_id: int):
    cafe_to_update = db.session.get(Cafe, cafe_id)
    if cafe_to_update:
        cafe_to_update.coffee_price = request.args.get('new_price')
        db.session.commit()
        return jsonify(response={'success': 'Successfully updated the price.'}), 200
    else:
        return jsonify(error={'Not Found': f'Sorry, no cafe with id={cafe_id} was found in the database.'}), 400


# HTTP DELETE - Delete Record
@app.route('/report_closed/<int:cafe_id>', methods=['DELETE'])
def delete_cafe(cafe_id: int):
    if SECRET_API_KEY == request.args.get('api_key'):
        cafe_to_delete = db.session.get(Cafe, cafe_id)
        if cafe_to_delete:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(response={'success': 'Successfully deleted the cafe.'}), 200
        else:
            return jsonify(error={'Not Found': f'Sorry, no cafe with id={cafe_id} was found in the database.'}), 404
    else:
        return jsonify(error={'Forbidden': 'Sorry, you are not allowed to perform this operation. Make sure you have the correct api_key.'})


if __name__ == '__main__':
    app.run(debug=True)
