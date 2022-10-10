from flaskr import create_app
from flaskr.config import ProductionConfig

app = create_app(ProductionConfig)
