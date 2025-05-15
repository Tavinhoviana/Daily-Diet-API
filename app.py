from flask import Flask, request, jsonify
from models.user import User
from database import db
from flask_login import LoginManager, login_user

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"

login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)

with app.app_context():
    db.create_all()
# View login

# Session <- conexao ativa

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Informe usuário e senha"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Usuário já existe"}), 400

    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Usuário registrado com sucesso"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Informe usuário e senha"}), 400

    user = User.query.filter_by(username=username).first()

    if user:
        login_user(user)
        return jsonify({"message": f"Bem-vindo, {user.username}!"})
    else:
        return jsonify({"message": "Usuário não encontrado"}), 404

if __name__ == "__main__":
    app.run(debug=True, port=5050)