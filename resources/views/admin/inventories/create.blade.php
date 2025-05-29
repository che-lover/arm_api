@extends('layouts.admin')
@section('content')
    <h1>Add Inventory</h1>
    <form action="{{ route('admin.inventories.store') }}" method="POST">
        @csrf
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
            <label>Photo URL</label>
            <input type="text" name="photo_url" class="form-control" value="{{ old('photo_url') }}">
            @error('photo_url')<div class="text-danger">{{ $message }}</div>@enderror
        </div>
        <button class="btn btn-success btn-sm">Save</button>
    </form>
@endsection
