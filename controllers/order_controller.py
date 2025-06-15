import os
import json
import uuid
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from models.order import Order, OrderSchema, db
from services.email_service import EmailService
from datetime import datetime

order_bp = Blueprint('orders', __name__, url_prefix='/api/orders')

# Khởi tạo schema
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

def allowed_file(filename):
    """Kiểm tra file có được phép upload không"""
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_order_number():
    """Tạo số đơn hàng unique"""
    while True:
        # Tạo số đơn hàng với format: ORD-YYYYMMDD-XXXX
        date_str = datetime.now().strftime('%Y%m%d')
        random_str = str(uuid.uuid4())[:8].upper()
        order_number = f"ORD-{date_str}-{random_str}"

        # Kiểm tra xem số đơn hàng đã tồn tại chưa
        existing_order = Order.query.filter_by(order_number=order_number).first()
        if not existing_order:
            return order_number

@order_bp.route('/', methods=['POST'])
def create_order():
    """
    Tạo đơn hàng mới
    """
    try:
        # Validate dữ liệu đầu vào
        json_data = request.get_json()
        if not json_data:
            return jsonify({'error': 'Không có dữ liệu JSON'}), 400
        
        # Tạo số đơn hàng tự động nếu không có
        if 'order_number' not in json_data or not json_data['order_number']:
            json_data['order_number'] = generate_unique_order_number()

        # Validate schema
        try:
            data = order_schema.load(json_data)
        except Exception as e:
            return jsonify({'error': f'Dữ liệu không hợp lệ: {str(e)}'}), 400

        # Kiểm tra số đơn hàng có bị trùng không
        existing_order = Order.query.filter_by(order_number=data['order_number']).first()
        if existing_order:
            # Tạo số đơn hàng mới nếu bị trùng
            data['order_number'] = generate_unique_order_number()

        # Tạo đơn hàng mới
        new_order = Order(
            warehouse_name=data['warehouse_name'],
            delivery_date=data['delivery_date'],
            delivery_method=data['delivery_method'],
            payment_method=data['payment_method'],
            goods_description=data['goods_description'],
            customer_email=data['customer_email'],
            customer_name=data['customer_name'],
            order_number=data['order_number'],
            bill_image_path=data.get('bill_image_path'),
            product_images=data.get('product_images'),
            status='pending'
        )
        
        # Lưu vào database
        db.session.add(new_order)
        db.session.commit()
        
        return jsonify({
            'message': 'Đơn hàng đã được tạo thành công',
            'order': order_schema.dump(new_order)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Lỗi khi tạo đơn hàng: {str(e)}")
        return jsonify({'error': f'Lỗi server: {str(e)}'}), 500

@order_bp.route('/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """
    Lấy thông tin đơn hàng theo ID
    """
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Không tìm thấy đơn hàng'}), 404
        
        return jsonify(order_schema.dump(order)), 200
        
    except Exception as e:
        current_app.logger.error(f"Lỗi khi lấy đơn hàng: {str(e)}")
        return jsonify({'error': f'Lỗi server: {str(e)}'}), 500

@order_bp.route('/', methods=['GET'])
def get_orders():
    """
    Lấy danh sách tất cả đơn hàng
    """
    try:
        orders = Order.query.all()
        return jsonify(orders_schema.dump(orders)), 200
        
    except Exception as e:
        current_app.logger.error(f"Lỗi khi lấy danh sách đơn hàng: {str(e)}")
        return jsonify({'error': f'Lỗi server: {str(e)}'}), 500

@order_bp.route('/<int:order_id>/upload-bill', methods=['POST'])
def upload_bill(order_id):
    """
    Upload file bill cho đơn hàng
    """
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Không tìm thấy đơn hàng'}), 404
        
        if 'file' not in request.files:
            return jsonify({'error': 'Không có file được upload'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Không có file được chọn'}), 400
        
        if file and allowed_file(file.filename):
            # Tạo thư mục upload nếu chưa có
            upload_folder = current_app.config['UPLOAD_FOLDER']
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            # Tạo tên file an toàn
            filename = secure_filename(f"bill_{order.order_number}_{file.filename}")
            file_path = os.path.join(upload_folder, filename)
            
            # Lưu file
            file.save(file_path)
            
            # Cập nhật đường dẫn trong database
            order.bill_image_path = file_path
            db.session.commit()
            
            return jsonify({
                'message': 'File bill đã được upload thành công',
                'file_path': file_path
            }), 200
        
        return jsonify({'error': 'File không hợp lệ'}), 400
        
    except Exception as e:
        current_app.logger.error(f"Lỗi khi upload bill: {str(e)}")
        return jsonify({'error': f'Lỗi server: {str(e)}'}), 500

@order_bp.route('/<int:order_id>/upload-products', methods=['POST'])
def upload_product_images(order_id):
    """
    Upload hình ảnh sản phẩm cho đơn hàng
    """
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Không tìm thấy đơn hàng'}), 404
        
        if 'files' not in request.files:
            return jsonify({'error': 'Không có file được upload'}), 400
        
        files = request.files.getlist('files')
        if not files or all(f.filename == '' for f in files):
            return jsonify({'error': 'Không có file được chọn'}), 400
        
        # Tạo thư mục upload nếu chưa có
        upload_folder = current_app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        uploaded_files = []
        
        for i, file in enumerate(files):
            if file and allowed_file(file.filename):
                # Tạo tên file an toàn
                filename = secure_filename(f"product_{order.order_number}_{i+1}_{file.filename}")
                file_path = os.path.join(upload_folder, filename)
                
                # Lưu file
                file.save(file_path)
                uploaded_files.append(file_path)
        
        if uploaded_files:
            # Cập nhật danh sách hình ảnh trong database
            order.product_images = json.dumps(uploaded_files)
            db.session.commit()
            
            return jsonify({
                'message': f'Đã upload thành công {len(uploaded_files)} file hình ảnh sản phẩm',
                'files': uploaded_files
            }), 200
        
        return jsonify({'error': 'Không có file hợp lệ nào được upload'}), 400
        
    except Exception as e:
        current_app.logger.error(f"Lỗi khi upload hình ảnh sản phẩm: {str(e)}")
        return jsonify({'error': f'Lỗi server: {str(e)}'}), 500

@order_bp.route('/<int:order_id>/send-notification', methods=['POST'])
def send_order_notification(order_id):
    """
    Gửi email thông báo đơn hàng
    """
    try:
        # Khởi tạo email service
        from flask_mail import Mail
        mail = Mail(current_app)
        email_service = EmailService(mail)
        
        # Gửi email
        result = email_service.send_order_notification(order_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        current_app.logger.error(f"Lỗi khi gửi email thông báo: {str(e)}")
        return jsonify({'error': f'Lỗi server: {str(e)}'}), 500
