import os

from app import create_app, setup_database
from app.tools.paths import DATABASE_FILE

app = create_app()


if __name__ == "__main__":
    # if os.path.isfile(DATABASE_FILE):
    #     os.remove(DATABASE_FILE)
    setup_database(app)
    app.run(debug=True)
