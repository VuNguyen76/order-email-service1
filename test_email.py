#!/usr/bin/env python3
"""
Script test cấu hình email
"""

import os
import sys
from flask import Flask
from flask_mail import Mail, Message
from config import Config

def test_email_config():
    """Test cấu hình email"""
    
    print("🔧 Đang test cấu hình email...")
    
    # Tạo Flask app
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Kiểm tra cấu hình
    required_configs = [
        'MAIL_SERVER',
        'MAIL_USERNAME', 
        'MAIL_PASSWORD',
        'MAIL_DEFAULT_SENDER'
    ]
    
    missing_configs = []
    for config in required_configs:
        if not app.config.get(config):
            missing_configs.append(config)
    
    if missing_configs:
        print("❌ Thiếu cấu hình:")
        for config in missing_configs:
            print(f"   - {config}")
        print("\n💡 Vui lòng tạo file .env và cấu hình email")
        return False

    # Kiểm tra cấu hình Gmail cụ thể
    username = app.config['MAIL_USERNAME']
    password = app.config['MAIL_PASSWORD']

    print(f"\n🔍 Kiểm tra cấu hình Gmail:")

    # Kiểm tra email format
    if not username.endswith('@gmail.com'):
        print(f"⚠️  Email không phải Gmail: {username}")

    # Kiểm tra App Password format
    if len(password) != 16 or ' ' in password:
        print("⚠️  Password có vẻ không phải App Password")
        print("💡 App Password Gmail có 16 ký tự, không có space")
        print("💡 Ví dụ: abcdefghijklmnop")

    # Kiểm tra MAIL_DEFAULT_SENDER
    if app.config['MAIL_DEFAULT_SENDER'] != username:
        print("⚠️  MAIL_DEFAULT_SENDER khác MAIL_USERNAME")
        print("💡 Nên để giống nhau cho Gmail")
    
    print("✅ Cấu hình email đã đầy đủ")
    print(f"📧 Mail Server: {app.config['MAIL_SERVER']}")
    print(f"👤 Username: {app.config['MAIL_USERNAME']}")
    print(f"📤 Default Sender: {app.config['MAIL_DEFAULT_SENDER']}")
    
    # Test gửi email
    with app.app_context():
        mail = Mail(app)
        
        try:
            print("\n📨 Đang gửi email test...")
            
            msg = Message(
                subject="Test Email từ Email Service",
                recipients=[app.config['MAIL_USERNAME']],  # Gửi cho chính mình
                body="Đây là email test từ Email Service. Nếu bạn nhận được email này, cấu hình đã thành công!",
                html="""
                <h2>🎉 Test Email Thành Công!</h2>
                <p>Chúc mừng! Cấu hình email của bạn đã hoạt động tốt.</p>
                <p>Bây giờ bạn có thể sử dụng Email Service để gửi thông báo đơn hàng.</p>
                <hr>
                <small>Email này được gửi từ Email Service</small>
                """
            )
            
            mail.send(msg)
            print("✅ Email test đã được gửi thành công!")
            print(f"📬 Kiểm tra hộp thư: {app.config['MAIL_USERNAME']}")
            return True
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Lỗi khi gửi email: {error_msg}")

            # Phân tích lỗi cụ thể
            if "Username and Password not accepted" in error_msg:
                print("\n🔧 LỖI GMAIL: Username/Password không được chấp nhận")
                print("💡 Nguyên nhân: Gmail không cho phép dùng password thường")
                print("✅ Giải pháp:")
                print("   1. Bật 2-Step Verification trong Google Account")
                print("   2. Tạo App Password (16 ký tự)")
                print("   3. Dùng App Password thay vì password thường")
                print("   4. Xem hướng dẫn chi tiết: fix_gmail_error.md")
            elif "Connection refused" in error_msg:
                print("\n🔧 LỖI KẾT NỐI: Không thể kết nối SMTP server")
                print("💡 Kiểm tra firewall hoặc network")
            elif "timeout" in error_msg.lower():
                print("\n🔧 LỖI TIMEOUT: Kết nối bị timeout")
                print("💡 Kiểm tra network hoặc thử port khác")
            else:
                print("\n💡 Các nguyên nhân có thể:")
                print("   - Sai username/password")
                print("   - Chưa bật App Password (Gmail)")
                print("   - Firewall chặn port 587")
                print("   - Cấu hình SMTP server sai")

            return False

def main():
    """Main function"""
    print("=" * 50)
    print("🧪 EMAIL SERVICE - TEST CẤU HÌNH")
    print("=" * 50)
    
    # Kiểm tra file .env
    if not os.path.exists('.env'):
        print("❌ Không tìm thấy file .env")
        print("💡 Chạy lệnh: cp .env.example .env")
        print("💡 Sau đó chỉnh sửa file .env với thông tin email của bạn")
        sys.exit(1)
    
    # Test cấu hình
    success = test_email_config()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 TEST THÀNH CÔNG!")
        print("🚀 Bạn có thể chạy ứng dụng: python app.py")
    else:
        print("❌ TEST THẤT BẠI!")
        print("📖 Xem hướng dẫn trong file: setup_email.md")
    print("=" * 50)

if __name__ == "__main__":
    main()
