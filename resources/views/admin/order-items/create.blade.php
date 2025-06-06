@extends('layouts.admin')
@section('content')
    <h1>Add Order Item</h1>
    <form action="{{ route('admin.order-items.store') }}" method="POST">
        @csrf
        <div class="mb-3">
            <label>Order ID</label>
            <input type="text" name="order_id" class="form-control" value="{{ old('order_id') }}">
            @error('order_id')<div class="text-danger">{{ $message }}</div>@enderror
        </div>
        <div class="mb-3">
            <label>Packaging ID</label>
            <input type="text" name="packaging_id" class="form-control" value="{{ old('packaging_id') }}">
            @error('packaging_id')<div class="text-danger">{{ $message }}</div>@enderror
        </div>
        <div class="mb-3">
            <label>Quantity</label>
            <input type="number" name="quantity" class="form-control" value="{{ old('quantity') }}">
            @error('quantity')<div class="text-danger">{{ $message }}</div>@enderror
        </div>
        <div class="mb-3">
            <label>Price</label>
            <input type="text" name="price" class="form-control" value="{{ old('price') }}">
            @error('price')<div class="text-danger">{{ $message }}</div>@enderror
        </div>
        <button class="btn btn-success btn-sm">Save</button>
    </form>
@endsection
