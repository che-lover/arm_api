@extends('layouts.admin')
@section('content')
    <h1>Add Packaging</h1>
    <form action="{{ route('admin.packagings.store') }}" method="POST">
        @csrf
        <div class="mb-3">
            <label>Product ID</label>
            <input type="text" name="product_id" class="form-control" value="{{ old('product_id') }}">
            @error('product_id')<div class="text-danger">{{ $message }}</div>@enderror
        </div>
        <div class="mb-3">
            <label>Volume</label>
            <input type="number" name="volume" class="form-control" value="{{ old('volume') }}">
            @error('volume')<div class="text-danger">{{ $message }}</div>@enderror
        </div>
        <div class="mb-3">
            <label>Price</label>
            <input type="text" name="price" class="form-control" value="{{ old('price') }}">
            @error('price')<div class="text-danger">{{ $message }}</div>@enderror
        </div>
        <button class="btn btn-success btn-sm">Save</button>
    </form>
@endsection
