@extends('layouts.admin')
@section('content')
    <h1>Add City</h1>
    <form action="{{ route('admin.cities.store') }}" method="POST">
        @csrf
        @foreach(['ru'=>'Русский','en'=>'English','hy'=>'Հայերեն'] as $lang=>$label)
            <div class="mb-3">
                <label class="form-label">Name ({{ $label }})</label>
                <input type="text" name="name_{{ $lang }}" class="form-control" value="{{ old('name_'.$lang) }}">
                @error('name_'.$lang)<div class="text-danger">{{ $message }}</div>@enderror
            </div>
        @endforeach
        <button class="btn btn-success btn-sm">Save</button>
    </form>
@endsection
