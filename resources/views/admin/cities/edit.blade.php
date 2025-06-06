@extends('layouts.admin')
@section('content')
    <h1>Edit City</h1>
    <form action="{{ route('admin.cities.update', $city) }}" method="POST">
        @csrf @method('PUT')
        @foreach(['ru'=>'Русский','en'=>'English','hy'=>'Հայերեն'] as $lang=>$label)
            <div class="mb-3">
                <label class="form-label">Name ({{ $label }})</label>
                <input type="text" name="name_{{ $lang }}" class="form-control" value="{{ old('name_'.$lang, $city['name_'.$lang]) }}">
                @error('name_'.$lang)<div class="text-danger">{{ $message }}</div>@enderror
            </div>
        @endforeach
        <button class="btn btn-primary btn-sm">Update</button>
    </form>
@endsection
