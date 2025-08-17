# web_ui/app.py
from flask import Flask
from web_ui.layout import layout_bp

app = Flask(__name__)
app.register_blueprint(layout_bp, url_prefix="/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8889, debug=True)
