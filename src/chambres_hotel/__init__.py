# Import des modules nécessaires depuis Flask
from flask import Flask
from flask_migrate import Migrate
from .database import db 

# Initialisation de l'extension Flask-Migrate pour la gestion des migrations de base de données
migrate = Migrate()

# Fonction de création de l'application Flask
def create_app():
    # Création de l'instance de l'application Flask
    app = Flask(__name__)
    # Configuration de l'application
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@<domaine|ip>:<port>/<database>'
    app.config['SECRET_KEY'] = 'mysecretkey'
    # Configuration de l'URI de la base de données
    # Ici, MySQL est utilisé comme moteur de base de données avec l'utilisateur 'root', le mot de passe 'pass', et la base de données 'chambres_hotel'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:pass@db/chambres_hotel'
    # Désactivation du suivi des modifications pour éviter les avertissements inutiles
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Initialisation de l'extension SQLAlchemy avec l'application
    db.init_app(app)
    # Initialisation de l'extension Flask-Migrate avec l'application et l'instance de la base de données
    migrate.init_app(app, db)
    # Importation et enregistrement des routes depuis le module routes.py
    from .routes import main
    app.register_blueprint(main)
    # Renvoi de l'instance de l'application Flask créée
    return app