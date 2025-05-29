@extends('layouts.admin')
@section('content')
    <h1>Edit Packaging</h1>
    <form action="{{ route('admin.packagings.update', $packaging) }}" method="POST">
        @csrf @method('PUT')
        <div class="mb-3">
            <label>Product ID</label>
            <input type="text" name="product_id" class="form-control" value="{{ old('product_id',$packaging->product_id) }}">
            @error('product_id')<div class="text-danger">{{ $message }}</div>@enderror
        </div>
        <div class="mb-3">
            <label>Volume</label>
            <input type="number" name="volume" class="form-control" value="{{ old('volume',$packaging->volume) }}">
            @error('volume')<div class="text-danger">{{ $message }}</div>@enderror
        </div>
        <div class="mb-3">
            <label>Price</label>
            <input type="text" name="price" class="form-control" value="{{ old('price',$packaging->price) }}">
            @error('price')<div class="text-danger">{{ $message }}</div>@enderror
        </div>
        <button class="btn btn-primary btn-sm">Update</button>
    </form>
@endsection
