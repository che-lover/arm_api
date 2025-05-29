@extends('layouts.admin')
@section('content')
    <h1>Edit Product</h1>
    <form action="{{ route('admin.products.update', $product) }}" method="POST">
        @csrf @method('PUT')
        @foreach(['ru'=>'Русский','en'=>'English','hy'=>'Հայերեն'] as $lang=>$label)
            <div class="mb-3">
                <label>Name ({{ $label }})</label>
                <input type="text" name="name_{{ $lang }}" class="form-control" value="{{ old('name_'.$lang, $product['name_'.$lang]) }}">
                @error('name_'.$lang)<div class="text-danger">{{ $message }}</div>@enderror
            </div>
        @endforeach
        <div class="mb-3">
            <label>Description (RU)</label>
            <textarea name="description_ru" class="form-control">{{ old('description_ru', $product->description_ru) }}</textarea>
            @error('description_ru')<div class="text-danger">{{ $message }}</div>@enderror
        </div>
        <div class="mb-3">
            <label>Description (EN)</label>
            <textarea name="description_en" class="form-control">{{ old('description_en', $product->description_en) }}</textarea>
            @error('description_en')<div class="text-danger">{{ $message }}</div>@enderror
        </div>
        <div class="mb-3">
            <label>Description (HY)</label>
            <textarea name="description_hy" class="form-control">{{ old('description_hy', $product->description_hy) }}</textarea>
            @error('description_hy')<div class="text-danger">{{ $message }}</div>@enderror
        </div>
        <button class="btn btn-primary btn-sm">Update</button>
    </form>
@endsection
