# Little Lemon API — Routes & Testing Guide
This document lists all available API endpoints, their roles, methods, purposes, and expected HTTP status codes for end-to-end testing.

# General Status Codes
HTTP Code	Meaning	Usage
200 OK	Success	For all successful GET, PUT, PATCH, and DELETE calls
201 Created	Created	For successful POST requests
400 Bad Request	Invalid Data	Validation failed for POST, PUT, PATCH, or DELETE
401 Forbidden	Authentication failed	No valid login or token
403 Unauthorized	Authorization failed	User not allowed to access resource
404 Not Found	Not found	Resource does not exist

# User Registration & Authentication (via Djoser)
Endpoint	Method	Role	Description	Example	Status
/api/users/	POST	Public	Create new user (register)	{ "username": "bob", "password": "1234" }	201
/api/users/me/	GET	Authenticated	Get current user info	Header → Bearer Token	200
/api/token/login/	POST	Public	Login with username & password, receive token	{ "username": "bob", "password": "1234" }	200

# Example Test (Insomnia):
POST /api/users/ → create user
POST /api/token/login/ → get token
Use token in all protected endpoints

# Menu Items Endpoints
Endpoint	Method	Role	Description	Expected Code
/api/menu-items/	GET	Customer, Delivery Crew, Manager	List all menu items	200
/api/menu-items/	POST	Manager	Create new menu item	201
/api/menu-items/{id}/	GET	Any Authenticated	Retrieve single menu item	200
/api/menu-items/{id}/	PUT / PATCH	Manager	Update a menu item	200
/api/menu-items/{id}/	DELETE	Manager	Delete a menu item	200
/api/menu-items/	POST / PUT / PATCH / DELETE	Customer / Delivery Crew	Not allowed	403

# Filter, Search, and Sort Examples
Feature	Example URL	Description
Filter	/api/menu-items/?price=5.50	Items with price = 5.50
Search	/api/menu-items/?search=pasta	Items with “pasta” in title or category
Order Ascending	/api/menu-items/?ordering=price	Low → High
Order Descending	/api/menu-items/?ordering=-price	High → Low

# User Group Management
1. Manager Group
Endpoint	Method	Role	Description	Status
/api/groups/manager/users	GET	Manager	List all managers	200
/api/groups/manager/users	POST	Manager	Add a user to manager group	201
/api/groups/manager/users/{userId}	DELETE	Manager	Remove user from manager group	200 / 404

2. Delivery Crew Group
Endpoint	Method	Role	Description	Status
/api/groups/delivery-crew/users	GET	Manager	List all delivery crew	200
/api/groups/delivery-crew/users	POST	Manager	Add a user to delivery crew group	201
/api/groups/delivery-crew/users/{userId}	DELETE	Manager	Remove user from delivery crew	200 / 404

# Testing Tip:
Use your manager’s Bearer token in Insomnia headers to perform POST/DELETE actions.

# Cart Management (Customer Only)
Endpoint	Method	Role	Description	Status
/api/cart/menu-items/	GET	Customer	View current cart	200
/api/cart/menu-items/	POST	Customer	Add item to cart	201
/api/cart/menu-items/	DELETE	Customer	Clear all items in cart	200
Example Request (POST):
{
  "menuitem_id": 3,
  "quantity": 2
}

# Order Management
1. For Customers
Endpoint	Method	Description	Status
/api/orders/	GET	Get all orders created by current user	200
/api/orders/	POST	Create order from current cart	201
/api/orders/{orderId}/	GET	Get order details (must belong to user)	200 / 403

2. For Managers
Endpoint	Method	Description	Status
/api/orders/	GET	View all orders from all users	200
/api/orders/{orderId}/	PUT / PATCH	Assign delivery crew or update order status	200
/api/orders/{orderId}/	DELETE	Delete order	200
3. For Delivery Crew
Endpoint	Method	Description	Status
/api/orders/	GET	Get all orders assigned to crew	200
/api/orders/{orderId}/	PATCH	Update order status (0 = out for delivery, 1 = delivered)	200

# Throttling & Pagination
Feature	Description	Example
Pagination	4 results per page	/api/menu-items/?page=2
Throttling	100 requests/day (anonymous)
1000 requests/day (authenticated)	Configured in settings.py


# Authentication Summary
Method	Header Example
Token	Authorization: Token <token>
JWT	Authorization: Bearer <token>
Session	Auto when logged in via /admin/

#  Quick End-to-End Test Checklist
Step	Action	Endpoint	Expected
1️⃣	Register new user	/api/users/	201
2️⃣	Get token	/api/token/login/	200
3️⃣	View menu items	/api/menu-items/	200
4️⃣	Try POST menu item as customer	/api/menu-items/	403
5️⃣	Add to cart	/api/cart/menu-items/	201
6️⃣	Create order	/api/orders/	201
7️⃣	View my orders	/api/orders/	200
8️⃣	Manager assigns delivery crew	/api/orders/{id}/	200
9️⃣	Delivery crew marks as delivered	/api/orders/{id}/	200

# Testing Tips in Insomnia
Always include your Authorization Header:
Authorization: Bearer <your_token_here>
For endpoints restricted to Manager or Delivery Crew, log in with that role’s credentials.
Check status codes carefully — they indicate if permissions and logic are set up correctly.
