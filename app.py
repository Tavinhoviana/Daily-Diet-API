from flask import Flask, request, jsonify
from models.user import User, Meal
from database import db
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from datetime import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:admin1234@127.0.0.1:3307/daily-diet"

login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)

# View login
login_manager.login_view = "login"

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    description = data.get("description")
    diet = data.get("diet")
    role = data.get("role", "user")

    if not username:
        return jsonify({"message": "Enter username"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "User already exists"}), 400

    new_user = User(
        username=username,
        description=description,
        diet=diet,
        role=role
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")

    if username:
        user = User.query.filter_by(username=username).first()

        if user:
            login_user(user)
            print(current_user.is_authenticated)
            return jsonify({"message": "Authentication completed successfully"})

    return jsonify({"message": "Invalid credentials"}), 400

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout successful"})

@app.route("/meals", methods=["POST"])
@login_required
def create_meal():

    data = request.get_json()

    name = data.get("name")
    description = data.get("description")
    datetime_str = data.get("datetime")
    is_on_diet = data.get("is_on_diet", False)

    if not name or not datetime_str:
        return jsonify({"message": "Missing required fields"}), 400

    try:
        meal_datetime = datetime.fromisoformat(datetime_str)
    except ValueError:
        return jsonify({"message": "Invalid datetime format"}), 400

    meal = Meal(
        name=name,
        description=description,
        datetime=meal_datetime,
        is_on_diet=is_on_diet,
        user_id=current_user.id
    )

    db.session.add(meal)
    db.session.commit()

    return jsonify({"message": "Meal created", "meal_id": meal.id}), 201

@app.route("/meal/<int:meal_id>", methods=["GET"])
@login_required
def check_meal(meal_id):

    meal = Meal.query.get(meal_id)

    if not meal:
        return jsonify({"message": "Meal not found"}), 404

    if meal.user_id != current_user.id:
        return jsonify({"message": "Not authorized"}), 403

    return jsonify({
        "id": meal.id,
        "name": meal.name,
        "description": meal.description,
        "datetime": meal.datetime.strftime("%Y-%m-%d %H:%M:%S"),
        "is_on_diet": meal.is_on_diet
    }), 200

@app.route("/user/<int:user_id>/meals", methods=["GET"])
@login_required
def get_user_meals(user_id):

    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    if current_user.id != user_id and current_user.role != "admin":
        return jsonify({"message": "Not authorized"}), 403

    meals = Meal.query.filter_by(user_id=user_id).all()

    meals_list = [{
        "id": meal.id,
        "name": meal.name,
        "description": meal.description,
        "datetime": meal.datetime.isoformat(),
        "is_on_diet": meal.is_on_diet,
    } for meal in meals]

    return jsonify({"meals": meals_list}), 200

@app.route("/user/<int:id_user>", methods=["PUT"])
@login_required
def update_user(id_user):
    data = request.json
    user = User.query.get(id_user)

    if not user:
        return jsonify({"message": "User not found"}), 404

    if "password" in data:
        user.password = data["password"]
    if "description" in data:
        user.description = data["description"]
    if "diet" in data:
        user.diet = data["diet"]

    db.session.commit()
    return jsonify({"message": f"User {id_user} successfully updated"})

@app.route("/meal/<int:meal_id>", methods=["PUT"])
@login_required
def edit_meal(meal_id):
    data = request.json

    meal = Meal.query.get(meal_id)

    if not meal:
        return jsonify({"message": "Meal not found"}), 404

    if meal.user_id != current_user.id:
        return jsonify({"message": "Not authorized"}), 403

    if "name" in data:
        meal.name = data["name"]
    if "description" in data:
        meal.description = data["description"]
    if "datetime" in data:
        try:
            meal.datetime = datetime.strptime(data["datetime"], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return jsonify({"message": "Invalid datetime format. Use YYYY-MM-DD HH:MM:SS"}), 400
    if "is_on_diet" in data:
        meal.is_on_diet = data["is_on_diet"]

    db.session.commit()

    return jsonify({"message": f"Meal {meal_id} updated successfully"}), 200

@app.route("/user/<int:id_user>/clear_description", methods=["PATCH"])
@login_required
def clear_user_description(id_user):
    user = User.query.get(id_user)
    if not user:
        return jsonify({"message": "User not found"}), 404
    if current_user.id != id_user and current_user.role != "admin":
        return jsonify({"message": "Not authorized"}), 403

    user.description = None
    db.session.commit()
    return jsonify({"message": f"Description of user {id_user} cleared successfully"}), 200

@app.route("/meal/<int:meal_id>", methods=["DELETE"])
@login_required
def delete_meal(meal_id):
    meal = Meal.query.get(meal_id)

    if not meal:
        return jsonify({"message": "Meal not found"}), 404

    if meal.user_id != current_user.id:
        return jsonify({"message": "Not authorized"}), 403

    db.session.delete(meal)
    db.session.commit()
    return jsonify({"message": f"Meal {meal_id} deleted successfully"}), 200

@app.route("/user/<int:id_user>", methods=["DELETE"])
@login_required
def delete_user(id_user):
    user = User.query.get(id_user)

    if current_user.role != "admin":
        return jsonify({"message": "Only admins can delete users"}), 403

    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted successfully"})

    return jsonify({"message": "User not found"}), 404

if __name__ == "__main__":
    app.run(debug=True, port=5050)