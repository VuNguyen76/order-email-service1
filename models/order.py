from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from marshmallow import Schema, fields

db = SQLAlchemy()

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    warehouse_name = db.Column(db.String(100), nullable=False)  # Tên kho gửi
    delivery_date = db.Column(db.Date, nullable=False)  # Ngày phát hàng
    delivery_method = db.Column(db.String(100), nullable=False)  # Hình thức giao nhận
    payment_method = db.Column(db.String(100), nullable=False)  # Hình thức thanh toán
    goods_description = db.Column(db.Text, nullable=False)  # Mô tả hàng hóa
    bill_image_path = db.Column(db.String(255))  # Đường dẫn file bill (jpg)
    product_images = db.Column(db.Text)  # JSON string chứa danh sách đường dẫn hình ảnh sản phẩm
    customer_email = db.Column(db.String(120), nullable=False)  # Email khách hàng
    customer_name = db.Column(db.String(100), nullable=False)  # Tên khách hàng
    order_number = db.Column(db.String(50), unique=True, nullable=False)  # Số đơn hàng
    status = db.Column(db.String(50), default='pending')  # Trạng thái đơn hàng
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Order {self.order_number}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'warehouse_name': self.warehouse_name,
            'delivery_date': self.delivery_date.strftime('%d.%m.%y') if self.delivery_date else None,
            'delivery_method': self.delivery_method,
            'payment_method': self.payment_method,
            'goods_description': self.goods_description,
            'bill_image_path': self.bill_image_path,
            'product_images': self.product_images,
            'customer_email': self.customer_email,
            'customer_name': self.customer_name,
            'order_number': self.order_number,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class OrderSchema(Schema):
    id = fields.Int(dump_only=True)
    warehouse_name = fields.Str(required=True)
    delivery_date = fields.Date(required=True)
    delivery_method = fields.Str(required=True)
    payment_method = fields.Str(required=True)
    goods_description = fields.Str(required=True)
    bill_image_path = fields.Str()
    product_images = fields.Str()
    customer_email = fields.Email(required=True)
    customer_name = fields.Str(required=True)
    order_number = fields.Str()  # Không bắt buộc, sẽ tự động tạo
    status = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
