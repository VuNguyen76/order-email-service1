#!/usr/bin/env python3
"""
Script để reset database - xóa tất cả dữ liệu và tạo lại bảng
"""

import os
from flask import Flask
from models.order import db
from config import Config

def reset_database():
    """Reset database"""
    
    print("🗑️  Đang reset database...")
    
    # Tạo Flask app
    app = Flask(__name__)
    app.config.from_object(Config)
    
    with app.app_context():
        # Khởi tạo database
        db.init_app(app)
        
        try:
            # Xóa tất cả bảng
            print("📋 Đang xóa tất cả bảng...")
            db.drop_all()
            
            # Tạo lại tất cả bảng
            print("🔨 Đang tạo lại bảng...")
            db.create_all()
            
            print("✅ Database đã được reset thành công!")
            print("🎯 Bây giờ bạn có thể tạo đơn hàng mới mà không bị lỗi trùng lặp")
            
        except Exception as e:
            print(f"❌ Lỗi khi reset database: {str(e)}")
            return False
    
    return True

def main():
    """Main function"""
    print("=" * 50)
    print("🔄 RESET DATABASE")
    print("=" * 50)
    
    # Xác nhận từ user
    confirm = input("⚠️  Bạn có chắc muốn xóa tất cả dữ liệu? (y/N): ")
    
    if confirm.lower() not in ['y', 'yes']:
        print("❌ Hủy bỏ reset database")
        return
    
    # Reset database
    success = reset_database()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 RESET THÀNH CÔNG!")
        print("🚀 Bạn có thể chạy ứng dụng: python app.py")
    else:
        print("❌ RESET THẤT BẠI!")
    print("=" * 50)

if __name__ == "__main__":
    main()
