<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Admin Panel</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container-fluid">
        <a class="navbar-brand" href="#">Admin</a>
        <div class="collapse navbar-collapse">
            <ul class="navbar-nav me-auto">
                <li class="nav-item"><a class="nav-link" href="{{ route('admin.cities.index') }}">Cities</a></li>
                <li class="nav-item"><a class="nav-link" href="{{ route('admin.districts.index') }}">Districts</a></li>
                <li class="nav-item"><a class="nav-link" href="{{ route('admin.products.index') }}">Products</a></li>
                <li class="nav-item"><a class="nav-link" href="{{ route('admin.packagings.index') }}">Packagings</a></li>
                <li class="nav-item"><a class="nav-link" href="{{ route('admin.inventories.index') }}">Inventory</a></li>
                <li class="nav-item"><a class="nav-link" href="{{ route('admin.coupons.index') }}">Coupons</a></li>
                <li class="nav-item"><a class="nav-link" href="{{ route('admin.orders.index') }}">Orders</a></li>
                <li class="nav-item"><a class="nav-link" href="{{ route('admin.order-items.index') }}">Order Items</a></li>
                <!-- другие пункты меню -->
            </ul>
            <form method="POST" action="">
                @csrf
                <button class="btn btn-outline-light" type="submit">Logout</button>
            </form>
        </div>
    </div>
</nav>
<div class="container mt-4">
    @if(session('success'))
        <div class="alert alert-success">{{ session('success') }}</div>
    @endif
    <div>
        @yield('content')
    </div>
</div>
</body>
</html>
