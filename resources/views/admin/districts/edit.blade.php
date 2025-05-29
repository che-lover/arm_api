@extends('layouts.admin')
@section('content')
    <h1>Edit District</h1>
    <form action="{{ route('admin.districts.update', $district) }}" method="POST">
        @csrf @method('PUT')
        <div class="mb-3">
            <label>City ID</label>
            <input type="text" name="city_id" class="form-control" value="{{ old('city_id', $district->city_id) }}">
            @error('city_id')<div class="text-danger">{{ $message }}</div>@enderror
        </div>
        @foreach(['ru'=>'Русский','en'=>'English','hy'=>'Հայերեն'] as $lang=>$label)
            <div class="mb-3">
                <label>Name ({{ $label }})</label>
                <input type="text" name="name_{{ $lang }}" class="form-control" value="{{ old('name_'.$lang, $district['name_'.$lang]) }}">
                @error('name_'.$lang)<div class="text-danger">{{ $message }}</div>@enderror
            </div>
        @endforeach
        <button class="btn btn-primary btn-sm">Update</button>
    </form>
@endsection
