# Admin Dashboard Backend Implementation

## Overview
Complete backend API endpoints for admin dashboard functionality with user, product, order, and settings management.

## Implemented Endpoints

### Admin Dashboard
- `GET /api/store/admin/dashboard/` - Dashboard overview with statistics

### Users Management  
- `GET /api/store/admin/users/` - List all users
- `POST /api/store/admin/users/` - Create new user
- `GET /api/store/admin/users/<id>/` - Get user details
- `PUT /api/store/admin/users/<id>/` - Update user
- `DELETE /api/store/admin/users/<id>/` - Delete user

### Products Management
- `GET /api/store/admin/products/` - List all products
- `POST /api/store/admin/products/` - Create new product
- `GET /api/store/admin/products/<id>/` - Get product details
- `PUT /api/store/admin/products/<id>/` - Update product
- `DELETE /api/store/admin/products/<id>/` - Delete product

### Orders Management
- `GET /api/store/admin/orders/` - List all orders
- `PATCH /api/store/admin/orders/<id>/` - Update order status
- `GET /api/store/admin/customers/` - List all customers

### Settings Management
- `GET /api/store/admin/settings/` - Get store settings
- `PUT /api/store/admin/settings/` - Update store settings

## Files Modified

### Backend (Django)
1. **store/views.py** - Added:
   - `admin_users()` - List/create users
   - `admin_user_detail()` - CRUD for individual users
   - `admin_products()` - List/create products
   - `admin_product_detail()` - CRUD for individual products
   - `admin_settings()` - Get/update store settings

2. **store/urls.py** - Updated with new admin endpoints

3. **store/serializers.py** - Fixed AdminUserSerializer to allow updates

### Frontend (React)
1. **src/pages/AdminDashboard.jsx** - Main admin dashboard page
2. **src/components/Admin/AdminOverview.jsx** - Dashboard statistics
3. **src/components/Admin/UserManagement.jsx** - User CRUD interface
4. **src/components/Admin/ProductManagement.jsx** - Product CRUD interface
5. **src/components/Admin/OrderManagement.jsx** - Order management interface
6. **src/components/Admin/AdminSettings.jsx** - Store settings management
7. **src/App.jsx** - Added admin route

## Key Features

✅ **User Management**
- View all users with statistics
- Create new users
- Edit user details and roles
- Delete users
- Search functionality

✅ **Product Management**
- List all products (including inactive)
- Add new products
- Edit product details
- Delete products
- Stock status tracking
- Product image handling

✅ **Order Management**
- View all orders
- Update order status (pending → processing → shipped → delivered)
- View order details and items
- Customer information display

✅ **Store Settings**
- Store information management
- Billing & shipping configuration
- Currency and tax settings
- Feature toggles (maintenance mode, registration)
- Danger zone for system operations

✅ **Dashboard Overview**
- Revenue analytics
- Order statistics
- Active users count
- Product inventory status
- Monthly revenue chart

## Security Features

🔒 All admin endpoints protected with `@permission_classes([IsAdminUser])`
- Only staff users can access admin features
- User cannot delete their own account
- Proper error handling and validation

## API Request/Response Examples

### Create User
```python
POST /api/store/admin/users/
{
    "username": "newadmin",
    "email": "admin@example.com",
    "password": "secure_password",
    "first_name": "John",
    "last_name": "Doe",
    "is_staff": true,
    "is_active": true
}
```

### Update Order Status
```python
PATCH /api/store/admin/orders/1/
{
    "status": "shipped"
}
```

### Update Settings
```python
PUT /api/store/admin/settings/
{
    "store_name": "My Store",
    "store_email": "support@mystore.com",
    "tax_rate": "15",
    "shipping_cost": "5.00",
    "maintenance_mode": false
}
```

## Frontend Access

Navigate to: `http://localhost:5173/admin`

Requires admin account to access.

## Notes

- Settings are cached using Django's cache framework
- All product and user operations include proper validation
- Orders support status updates with audit trail
- Images handled through Cloudinary integration
- Responsive design for desktop and tablet viewing
