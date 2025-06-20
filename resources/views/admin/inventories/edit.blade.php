@extends('layouts.admin')
@section('content')
    <h1>Edit Inventory</h1>
    <form action="{{ route('admin.inventories.update',$inventory) }}" method="POST">
        @csrf @method('PUT')
        <div class="mb-3">
            <label>City ID</label>
            <input type="text" name="city_id" class="form-control" value="{{ old('city_id',$inventory->city_id) }}">
            @error('city_id')<div class="text-danger">{{ $message }}</div>@enderror
        </div>
        <div class="mb-3">
            <label>District ID</label>
            <input type="text" name="district_id" class="form-control" value="{{ old('district_id',$inventory->district_id) }}">
            @error('district_id')<div class="text-danger">{{ $message }}</div>@enderror
        </div>
        <div class="mb-3">
            <label>Packaging ID</label>
            <input type="text" name="packaging_id" class="form-control" value="{{ old('packaging_id',$inventory->packaging_id) }}">
            @error('packaging_id')<div class="text-danger">{{ $message }}</div>@enderror
        </div>
        <div class="mb-3">
            <label>Quantity</label>
            <input type="number" name="quantity" class="form-control" value="{{ old('quantity',$inventory->quantity) }}">
            @error('quantity')<div class="text-danger">{{ $message }}</div>@enderror
        </div>
        <div class="mb-3">
            <label>Status (pending/confirmed)</label>
            <input type="text" name="status" class="form-control" value="{{ old('status',$inventory->status) }}">
            @error('quantity')<div class="text-danger">{{ $message }}</div>@enderror
        </div>
        <div class="mb-3">
            <label>Photo URL</label>
            <input type="text" name="photo_url" class="form-control" value="{{ old('photo_url',$inventory->photo_url) }}">
            @error('photo_url')<div class="text-danger">{{ $message }}</div>@enderror
        </div>
        <button class="btn btn-primary btn-sm">Update</button>
    </form>
@endsection
