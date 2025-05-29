@extends('layouts.admin')
@section('content')
    <h1>Add Coupon</h1>
    <form action="{{ route('admin.coupons.store') }}" method="POST">
        @csrf
        <div class="mb-3">
            <label>Code</label>
            <input type="text" name="code" class="form-control" value="{{ old('code') }}">
            @error('code')<div class="text-danger">{{ $message }}</div>@enderror
        </div>
        <div class="mb-3">
            <label>Discount Amount</label>
            <input type="text" name="discount_amount" class="form-control" value="{{ old('discount_amount') }}">
            @error('discount_amount')<div class="text-danger">{{ $message }}</div>@enderror
        </div>
        <div class="mb-3">
            <label>Expires At</label>
            <input type="datetime-local" name="expires_at" class="form-control" value="{{ old('expires_at') }}">
            @error('expires_at')<div class="text-danger">{{ $message }}</div>@enderror
        </div>
        <div class="form-check mb-3">
            <input type="checkbox" name="used" class="form-check-input" value="1" {{ old('used') ? 'checked' : '' }}>
            <label class="form-check-label">Used</label>
        </div>
        <button class="btn btn-success btn-sm">Save</button>
    </form>
@endsection
