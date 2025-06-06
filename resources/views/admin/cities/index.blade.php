@extends('layouts.admin')
@section('content')
    <div class="d-flex justify-content-between align-items-center mb-3">
        <h1>Cities</h1>
        <a href="{{ route('admin.cities.create') }}" class="btn btn-primary">Add City</a>
    </div>
    <table class="table table-bordered">
        <thead><tr><th>ID</th><th>Name (RU)</th><th>Name (EN)</th><th>Name (HY)</th><th>Actions</th></tr></thead>
        <tbody>
        @foreach($cities as $city)
            <tr>
                <td>{{ $city->id }}</td>
                <td>{{ $city->name_ru }}</td>
                <td>{{ $city->name_en }}</td>
                <td>{{ $city->name_hy }}</td>
                <td>
                    <a href="{{ route('admin.cities.edit', $city) }}" class="btn btn-sm btn-warning">Edit</a>
                    <form action="{{ route('admin.cities.destroy', $city) }}" method="POST" class="d-inline">
                        @csrf @method('DELETE')
                        <button class="btn btn-sm btn-danger" onclick="return confirm('Delete?')">Delete</button>
                    </form>
                </td>
            </tr>
        @endforeach
        </tbody>
    </table>
    {{ $cities->links('pagination::simple-bootstrap-5') }}
@endsection
