@extends('layouts.admin')
@section('content')
    <h1>Edit Coupon</h1>
    <form action="{{ route('admin.coupons.update',$coupon) }}" method="POST">
        @csrf @method('PUT')
        <div class="mb-3">
            <label>Code</label>
            <input type="text" name="code" class="form-control" value="{{ old('code',$coupon->code) }}">
            @error('code')<div class="text-danger">{{ $message }}</div>@enderror
        </div>
        <div class="mb-3">
            <label>Discount Amount</label>
            <input type="text" name="discount_amount" class="form-control" value="{{ old('discount_amount',$coupon->discount_amount) }}">
            @error('discount_amount')<div class="text-danger">{{ $message }}</div>@enderror
        </div>
        <div class="mb-3">
            <label>Expires At</label>
            <input type="datetime-local" name="expires_at" class="form-control" value="{{ old('expires_at',$coupon->expires_at) }}">
            @error('expires_at')<div class="text-danger">{{ $message }}</div>@enderror
        </div>
        <div class="form-check mb-3">
            <input type="checkbox" name="used" class="form-check-input" value="1" {{ $coupon->used ? 'checked' : '' }}>
            <label class="form-check-label">Used</label>
        </div>
        <button class="btn btn-primary btn-sm">Update</button>
    </form>
@endsection
