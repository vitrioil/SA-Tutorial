import os
from blog import create_config_app

app = create_config_app()

if not os.path.exists("blog/site.db"):
    print("Creating database")
    from blog import db
    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
