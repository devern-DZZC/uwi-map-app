from App.database import db


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    body = db.Column(db.String(1024), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    replies = db.relationship("Reply", backref="review", lazy=True)

    def __init__(self, product_id, user_id, body, timestamp):
        self.product_id = product_id
        self.user_id = user_id
        self.body = body
        self.timestamp = timestamp

    def to_json(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "user_id": self.user_id,
            "body": self.body,
            "timestamp": self.timestamp,
        }
