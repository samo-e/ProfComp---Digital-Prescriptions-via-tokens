from website import create_app, db
from website.models import User

app = create_app()

with app.app_context():
    num_deleted = User.query.delete()
    db.session.commit()
    print(f"Deleted {num_deleted} users from the database.")
