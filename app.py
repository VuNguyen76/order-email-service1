import os
from flask import Flask, render_template
from flask_mail import Mail
from config import Config
from models.order import db
from controllers.order_controller import order_bp

def create_app():
    """
    Factory function để tạo Flask app
    """
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Khởi tạo extensions
    db.init_app(app)
    mail = Mail(app)
    
    # Đăng ký blueprints
    app.register_blueprint(order_bp)
    
    # Tạo bảng database
    with app.app_context():
        db.create_all()
        
        # Tạo thư mục upload nếu chưa có
        upload_folder = app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
    
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/api')
    def api_info():
        return {
            'message': 'Email Service API',
            'version': '1.0.0',
            'endpoints': {
                'create_order': 'POST /api/orders/',
                'get_order': 'GET /api/orders/<id>',
                'get_orders': 'GET /api/orders/',
                'upload_bill': 'POST /api/orders/<id>/upload-bill',
                'upload_products': 'POST /api/orders/<id>/upload-products',
                'send_notification': 'POST /api/orders/<id>/send-notification'
            }
        }
    
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Endpoint không tồn tại'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Lỗi server nội bộ'}, 500
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
