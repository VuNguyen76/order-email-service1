// Global variables
let billFile = null;
let qrFile = null;
let productFiles = [];

// DOM elements
const billUploadArea = document.getElementById('billUploadArea');
const qrUploadArea = document.getElementById('qrUploadArea');
const productUploadArea = document.getElementById('productUploadArea');
const billFileInput = document.getElementById('billFile');
const qrFileInput = document.getElementById('qrFile');
const productFilesInput = document.getElementById('productFiles');
const orderForm = document.getElementById('orderForm');

// Initialize event listeners
document.addEventListener('DOMContentLoaded', function() {
    setupFileUpload();
    setupForm();
});

function setupFileUpload() {
    // Bill file upload
    setupSingleFileUpload(billUploadArea, billFileInput, 'billPreview', (file) => {
        billFile = file;
    });

    // QR file upload
    setupSingleFileUpload(qrUploadArea, qrFileInput, 'qrPreview', (file) => {
        qrFile = file;
    });

    // Product files upload
    setupMultipleFileUpload(productUploadArea, productFilesInput, 'productPreview', (files) => {
        productFiles = files;
    });
}

function setupSingleFileUpload(uploadArea, fileInput, previewId, callback) {
    // Click to upload
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            callback(file);
            showPreview([file], previewId, true);
        }
    });

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = Array.from(e.dataTransfer.files);
        if (files.length > 0 && files[0].type.startsWith('image/')) {
            callback(files[0]);
            showPreview([files[0]], previewId, true);
        }
    });
}

function setupMultipleFileUpload(uploadArea, fileInput, previewId, callback) {
    // Click to upload
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        const files = Array.from(e.target.files);
        if (files.length > 0) {
            productFiles = [...productFiles, ...files];
            callback(productFiles);
            showPreview(productFiles, previewId, false);
        }
    });

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = Array.from(e.dataTransfer.files).filter(file => file.type.startsWith('image/'));
        if (files.length > 0) {
            productFiles = [...productFiles, ...files];
            callback(productFiles);
            showPreview(productFiles, previewId, false);
        }
    });
}

function showPreview(files, previewId, isSingle) {
    const previewContainer = document.getElementById(previewId);
    
    if (isSingle) {
        previewContainer.innerHTML = '';
    }
    
    files.forEach((file, index) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            const previewItem = document.createElement('div');
            previewItem.className = 'preview-item';
            previewItem.innerHTML = `
                <img src="${e.target.result}" alt="Preview">
                <button type="button" class="remove-btn" onclick="removeFile('${previewId}', ${index}, ${isSingle})">
                    <i class="fas fa-times"></i>
                </button>
            `;
            
            if (isSingle) {
                previewContainer.innerHTML = '';
                previewContainer.appendChild(previewItem);
            } else {
                previewContainer.appendChild(previewItem);
            }
        };
        reader.readAsDataURL(file);
    });
}

function removeFile(previewId, index, isSingle) {
    if (isSingle) {
        if (previewId === 'billPreview') {
            billFile = null;
        } else if (previewId === 'qrPreview') {
            qrFile = null;
        }
        document.getElementById(previewId).innerHTML = '';
    } else {
        productFiles.splice(index, 1);
        showPreview(productFiles, previewId, false);
    }
}

function setupForm() {
    orderForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Show loading state
        const submitBtn = orderForm.querySelector('button[type="submit"]');
        const loadingSpan = submitBtn.querySelector('.loading');
        const normalSpan = submitBtn.querySelector('.normal-text');
        
        loadingSpan.style.display = 'inline';
        normalSpan.style.display = 'none';
        submitBtn.disabled = true;
        
        try {
            // Create order
            const orderData = {
                customer_name: document.getElementById('customerName').value,
                customer_email: document.getElementById('customerEmail').value,
                warehouse_name: document.getElementById('warehouseName').value,
                delivery_date: document.getElementById('deliveryDate').value,
                delivery_method: document.getElementById('deliveryMethod').value,
                payment_method: document.getElementById('paymentMethod').value,
                goods_description: document.getElementById('goodsDescription').value
            };

            // Thêm order_number nếu có nhập
            const orderNumber = document.getElementById('orderNumber').value.trim();
            if (orderNumber) {
                orderData.order_number = orderNumber;
            }
            
            const orderResponse = await fetch('/api/orders/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(orderData)
            });
            
            if (!orderResponse.ok) {
                throw new Error('Không thể tạo đơn hàng');
            }
            
            const orderResult = await orderResponse.json();
            const orderId = orderResult.order.id;
            
            // Upload bill file
            if (billFile) {
                await uploadFile(orderId, 'bill', billFile);
            }
            
            // Upload QR file (treat as product image)
            if (qrFile) {
                await uploadFile(orderId, 'products', [qrFile]);
            }
            
            // Upload product files
            if (productFiles.length > 0) {
                const allProductFiles = qrFile ? [qrFile, ...productFiles] : productFiles;
                await uploadFile(orderId, 'products', allProductFiles);
            }
            
            // Send notification email
            const notificationResponse = await fetch(`/api/orders/${orderId}/send-notification`, {
                method: 'POST'
            });
            
            if (!notificationResponse.ok) {
                throw new Error('Không thể gửi email thông báo');
            }
            
            showAlert('success', 'Email thông báo đã được gửi thành công!');
            resetForm();
            
        } catch (error) {
            console.error('Error:', error);
            showAlert('danger', `Lỗi: ${error.message}`);
        } finally {
            // Hide loading state
            loadingSpan.style.display = 'none';
            normalSpan.style.display = 'inline';
            submitBtn.disabled = false;
        }
    });
}

async function uploadFile(orderId, type, files) {
    const formData = new FormData();
    
    if (type === 'bill') {
        formData.append('file', files);
        const response = await fetch(`/api/orders/${orderId}/upload-bill`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Không thể upload file bill');
        }
    } else if (type === 'products') {
        files.forEach(file => {
            formData.append('files', file);
        });
        
        const response = await fetch(`/api/orders/${orderId}/upload-products`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Không thể upload hình ảnh sản phẩm');
        }
    }
}

function showAlert(type, message) {
    const alertContainer = document.getElementById('alertContainer');
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.appendChild(alertDiv);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function resetForm() {
    orderForm.reset();
    billFile = null;
    qrFile = null;
    productFiles = [];
    
    document.getElementById('billPreview').innerHTML = '';
    document.getElementById('qrPreview').innerHTML = '';
    document.getElementById('productPreview').innerHTML = '';
}
