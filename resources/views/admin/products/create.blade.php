@extends('layouts.admin')
@section('content')
    <h1>Add Product</h1>
    <form action="{{ route('admin.products.store') }}" method="POST">
        @csrf
        @foreach(['ru'=>'Русский','en'=>'English','hy'=>'Հայերեն'] as $lang=>$label)
            <div class="mb-3">
                <label>Name ({{ $label }})</label>
                <input type="text" name="name_{{ $lang }}" class="form-control" value="{{ old('name_'.$lang) }}">
                @error('name_'.$lang)<div class="text-danger">{{ $message }}</div>@enderror
            </div>
            <div class="mb-3">
                <label>Description</label>
                <textarea name="description_ru" class="form-control" placeholder="RU">{{ old('description_ru') }}</textarea>
                <textarea name="description_en" class="form-control mt-2" placeholder="EN">{{ old('description_en') }}</textarea>
                <textarea name="description_hy" class="form-control mt-2" placeholder="HY">{{ old('description_hy') }}</textarea>
            </div>
        @endforeach
            <button class="btn btn-success btn-sm">Save</button>
    </form>
@endsection
