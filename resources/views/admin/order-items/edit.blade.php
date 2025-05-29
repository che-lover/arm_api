<!-- resources/views/admin/order-items/edit.blade.php -->
@extends('layouts.admin')

@section('content')
    <h1>Edit Order Item #{{ $orderItem->id }}</h1>

    <form action="{{ route('admin.order-items.update', $orderItem) }}" method="POST">
        @csrf
        @method('PUT')

        <div class="mb-3">
            <label for="order_id">Order ID</label>
            <input id="order_id"
                   type="text"
                   name="order_id"
                   class="form-control"
                   value="{{ old('order_id', $orderItem->order_id) }}">
            @error('order_id')
            <div class="text-danger">{{ $message }}</div>
            @enderror
        </div>

        <div class="mb-3">
            <label for="packaging_id">Packaging ID</label>
            <input id="packaging_id"
                   type="text"
                   name="packaging_id"
                   class="form-control"
                   value="{{ old('packaging_id', $orderItem->packaging_id) }}">
            @error('packaging_id')
            <div class="text-danger">{{ $message }}</div>
            @enderror
        </div>

        <div class="mb-3">
            <label for="quantity">Quantity</label>
            <input id="quantity"
                   type="number"
                   name="quantity"
                   class="form-control"
                   value="{{ old('quantity', $orderItem->quantity) }}">
            @error('quantity')
            <div class="text-danger">{{ $message }}</div>
            @enderror
        </div>

        <div class="mb-3">
            <label for="price">Price</label>
            <input id="price"
                   type="text"
                   name="price"
                   class="form-control"
                   value="{{ old('price', $orderItem->price) }}">
            @error('price')
            <div class="text-danger">{{ $message }}</div>
            @enderror
        </div>

        <button class="btn btn-primary btn-sm">Update</button>
        <a href="{{ route('admin.order-items.index') }}" class="btn btn-secondary btn-sm">Back to list</a>
    </form>
@endsection
