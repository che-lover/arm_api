@extends('layouts.admin')
@section('content')
    <h1>Edit Order</h1>
    <form action="{{ route('admin.orders.update',$order) }}" method="POST">
        @csrf @method('PUT')
        <div class="mb-3">
            <label>User ID</label>
            <input type="text" name="user_id" class="form-control" value="{{ old('user_id',$order->user_id) }}">
            @error('user_id')<div class="text-danger">{{ $message }}</div>@enderror
        </div>
        <div class="mb-3">
            <label>Total Amount</label>
            <input type="text" name="total_amount" class="form-control" value="{{ old('total_amount',$order->total_amount) }}">
            @error('total_amount')<div class="text-danger">{{ $message }}</div>@enderror
        </div>
        <div class="mb-3">
            <label>Status</label>
            <input type="text" name="status" class="form-control" value="{{ old('status',$order->status) }}">
            @error('status')<div class="text-danger">{{ $message }}</div>@enderror
        </div>
        <button class="btn btn-primary btn-sm">Update</button>
    </form>
@endsection
