## Tính năng

- 🎨 **Giao diện web đẹp** - UI hiện đại, responsive
- 📦 **Tạo và quản lý đơn hàng**
- 🧾 **Upload file bill** (JPG/PNG)
- 📱 **Upload QR code hóa đơn**
- 🖼️ **Upload hình ảnh sản phẩm** (multiple files)
- 📧 **Gửi email thông báo** với định dạng tiếng Việt
- 📎 **Đính kèm file** bill, QR code và hình ảnh sản phẩm
- 🎯 **Drag & Drop** upload files

## Cài đặt
1. Clone repository
2. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

3. Tạo file `.env` từ `.env.example` và cấu hình:
```bash
cp .env.example .env
```

4. Chỉnh sửa file `.env` với thông tin email của bạn

5. Test cấu hình email:
```bash
python test_email.py
```

6. Chạy ứng dụng:
```bash
python app.py
```

7. Reset database nếu cần (xóa dữ liệu cũ):
```bash
python reset_database.py
```

8. Truy cập giao diện web:
```
http://localhost:5000
```
## API Endpoints

### 1. Tạo đơn hàng
```
POST /api/orders/
```

Body:
```json
{
    "warehouse_name": "Kho Hà Nội",
    "delivery_date": "2024-12-25",
    "delivery_method": "Giao hàng tận nơi",
    "payment_method": "Chuyển khoản",
    "goods_description": "Điện thoại iPhone 15 Pro Max",
    "customer_email": "customer@example.com",
    "customer_name": "Nguyễn Văn A",
    "order_number": "ORD001"
}
```

### 2. Upload file bill
```
POST /api/orders/{order_id}/upload-bill
```
Form-data: file (JPG/JPEG/PNG)

### 3. Upload hình ảnh sản phẩm
```
POST /api/orders/{order_id}/upload-products
```
Form-data: files[] (multiple JPG/JPEG/PNG files)

### 4. Gửi email thông báo
```
POST /api/orders/{order_id}/send-notification
```

### 5. Lấy thông tin đơn hàng
```
GET /api/orders/{order_id}
```

### 6. Lấy danh sách đơn hàng
```
GET /api/orders/
```

## Cấu hình Email

Để sử dụng Gmail, bạn cần:
1. Bật 2-factor authentication
2. Tạo App Password
3. Sử dụng App Password trong file .env
