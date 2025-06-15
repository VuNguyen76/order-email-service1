import os
import json
from flask import current_app
from flask_mail import Mail, Message
from models.order import Order
from datetime import datetime

class EmailService:
    def __init__(self, mail_instance):
        self.mail = mail_instance
    
    def send_order_notification(self, order_id):
        """
        Gửi email thông báo đơn hàng
        """
        try:
            # Lấy thông tin đơn hàng
            order = Order.query.get(order_id)
            if not order:
                raise ValueError(f"Không tìm thấy đơn hàng với ID: {order_id}")
            
            # Tạo nội dung email
            subject = f"Thông báo đơn hàng #{order.order_number}"
            
            # Tạo nội dung email HTML
            html_body = self._create_email_html_content(order)
            
            # Tạo nội dung email text
            text_body = self._create_email_text_content(order)
            
            # Tạo message
            msg = Message(
                subject=subject,
                recipients=[order.customer_email],
                html=html_body,
                body=text_body
            )
            
            # Đính kèm file bill nếu có
            if order.bill_image_path and os.path.exists(order.bill_image_path):
                with current_app.open_resource(order.bill_image_path) as fp:
                    msg.attach(
                        filename=f"bill_{order.order_number}.jpg",
                        content_type="image/jpeg",
                        data=fp.read()
                    )
            
            # Đính kèm hình ảnh sản phẩm nếu có
            if order.product_images:
                try:
                    product_image_paths = json.loads(order.product_images)
                    for i, image_path in enumerate(product_image_paths):
                        if os.path.exists(image_path):
                            with current_app.open_resource(image_path) as fp:
                                filename = f"product_{order.order_number}_{i+1}.jpg"
                                msg.attach(
                                    filename=filename,
                                    content_type="image/jpeg",
                                    data=fp.read()
                                )
                except json.JSONDecodeError:
                    current_app.logger.warning(f"Không thể parse product_images cho đơn hàng {order.order_number}")
            
            # Gửi email
            self.mail.send(msg)
            
            # Cập nhật trạng thái đơn hàng
            order.status = 'notified'
            from models.order import db
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Email thông báo đã được gửi thành công đến {order.customer_email}'
            }
            
        except Exception as e:
            current_app.logger.error(f"Lỗi khi gửi email: {str(e)}")
            return {
                'success': False,
                'message': f'Lỗi khi gửi email: {str(e)}'
            }
    
    def _create_email_html_content(self, order):
        """
        Tạo nội dung email HTML
        """
        delivery_date_formatted = order.delivery_date.strftime('%d.%m.%y')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Thông báo đơn hàng</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #f4f4f4; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .info-row {{ margin: 10px 0; }}
                .label {{ font-weight: bold; color: #555; }}
                .footer {{ background-color: #f4f4f4; padding: 15px; text-align: center; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Thông báo đơn hàng #{order.order_number}</h2>
                </div>
                
                <div class="content">
                    <p>Kính chào {order.customer_name},</p>
                    
                    <p>Chúng tôi xin thông báo thông tin đơn hàng của bạn:</p>
                    
                    <div class="info-row">
                        <span class="label">Kho gửi:</span> {order.warehouse_name}
                    </div>
                    
                    <div class="info-row">
                        <span class="label">Ngày phát:</span> {delivery_date_formatted}
                    </div>
                    
                    <div class="info-row">
                        <span class="label">Hình thức giao nhận:</span> {order.delivery_method}
                    </div>
                    
                    <div class="info-row">
                        <span class="label">Hình thức thanh toán:</span> {order.payment_method}
                    </div>
                    
                    <div class="info-row">
                        <span class="label">Mô tả hàng hóa:</span><br>
                        {order.goods_description}
                    </div>
                    
                    <p>Vui lòng kiểm tra các file đính kèm để xem chi tiết bill và hình ảnh sản phẩm.</p>
                    
                    <p>Cảm ơn bạn đã sử dụng dịch vụ của chúng tôi!</p>
                </div>
                
                <div class="footer">
                    <p>Email này được gửi tự động, vui lòng không trả lời.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _create_email_text_content(self, order):
        """
        Tạo nội dung email text thuần
        """
        delivery_date_formatted = order.delivery_date.strftime('%d.%m.%y')
        
        text_content = f"""
Thông báo đơn hàng #{order.order_number}

Kính chào {order.customer_name},

Chúng tôi xin thông báo thông tin đơn hàng của bạn:

Kho gửi: {order.warehouse_name}
Ngày phát: {delivery_date_formatted}
Hình thức giao nhận: {order.delivery_method}
Hình thức thanh toán: {order.payment_method}
Mô tả hàng hóa: {order.goods_description}

Vui lòng kiểm tra các file đính kèm để xem chi tiết bill và hình ảnh sản phẩm.

Cảm ơn bạn đã sử dụng dịch vụ của chúng tôi!

---
Email này được gửi tự động, vui lòng không trả lời.
        """
        
        return text_content
