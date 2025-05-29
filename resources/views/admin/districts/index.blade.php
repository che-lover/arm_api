@extends('layouts.admin')
@section('content')
    <div class="d-flex justify-content-between mb-3">
        <h1>Districts</h1>
        <a href="{{ route('admin.districts.create') }}" class="btn btn-primary btn-sm">Add District</a>
    </div>
    <table class="table table-striped">
        <thead><tr><th>#</th><th>City ID</th><th>Name RU</th><th>Name EN</th><th>Name HY</th><th>Actions</th></tr></thead>
        <tbody>
        @foreach($items as $district)
            <tr>
                <td>{{ $district->id }}</td>
                <td>{{ $district->city->name_ru }}</td>
                <td>{{ $district->name_ru }}</td>
                <td>{{ $district->name_en }}</td>
                <td>{{ $district->name_hy }}</td>
                <td>
                    <a href="{{ route('admin.districts.edit',$district) }}" class="btn btn-warning btn-sm">Edit</a>
                    <form action="{{ route('admin.districts.destroy',$district) }}" method="POST" class="d-inline">
                        @csrf @method('DELETE')
                        <button class="btn btn-danger btn-sm">Delete</button>
                    </form>
                </td>
            </tr>
        @endforeach
        </tbody>
    </table>
    <div>{!! $items->links('pagination::simple-bootstrap-5') !!}</div>
@endsection
