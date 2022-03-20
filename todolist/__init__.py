from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = 'c0bdaf3f96938927083e9f7a11882e43'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
loginManager = LoginManager(app)
loginManager.login_view = 'login_page'


from todolist import routes



# from todolist.config import Config
# def createApp(config_class=Config):
#     app = Flask(__name__)
#     app.config.from_object(Config)

#     db.init_app(app)
#     bcrypt.init_app(app) 
#     loginManager.init_app(app)
#     mail.init_app(app)

#     # to avoid circular imports
    
#     from flaskblog.users.routes import users
#     from flaskblog.posts.routes import posts
#     from flaskblog.main.routes import main
#     from flaskblog.errors.handlers import errors

#     app.register_blueprint(users)
#     app.register_blueprint(posts)
#     app.register_blueprint(main)
#     app.register_blueprint(errors)

#     return app