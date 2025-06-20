@extends('layouts.admin')
@section('content')
    <h1>Add Order</h1>
    <form action="{{ route('admin.orders.store') }}" method="POST">
        @csrf
        <div class="mb-3">
            <label>User ID</label>
            <input type="text" name="user_id" class="form-control" value="{{ old('user_id') }}">
            @error('user_id')<div class="text-danger">{{ $message }}</div>@enderror
        </div>
        <div class="mb-3">
            <label>City ID</label>
            <input type="text" name="city_id" class="form-control" value="{{ old('city_id') }}">
            @error('city_id')<div class="text-danger">{{ $message }}</div>@enderror
        </div>
        <div class="mb-3">
            <label>District ID</label>
            <input type="text" name="district_id" class="form-control" value="{{ old('district_id') }}">
            @error('district_id')<div class="text-danger">{{ $message }}</div>@enderror
        </div>
        <div class="mb-3">
            <label>Total Amount</label>
            <input type="text" name="total_amount" class="form-control" value="{{ old('total_amount') }}">
            @error('total_amount')<div class="text-danger">{{ $message }}</div>@enderror
        </div>
        <div class="mb-3">
            <label>Status</label>
            <input type="text" name="status" class="form-control" value="{{ old('status') }}">
            @error('status')<div class="text-danger">{{ $message }}</div>@enderror
        </div>
        <button class="btn btn-success btn-sm">Save</button>
    </form>
@endsection
