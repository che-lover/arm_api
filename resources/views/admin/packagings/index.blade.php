@extends('layouts.admin')
@section('content')
    <div class="d-flex justify-content-between mb-3">
        <h1>Packagings</h1>
        <a href="{{ route('admin.packagings.create') }}" class="btn btn-primary btn-sm">Add Packaging</a>
    </div>
    <table class="table table-striped">
        <thead><tr><th>#</th><th>Product</th><th>Volume</th><th>Price</th><th>Actions</th></tr></thead>
        <tbody>
        @foreach($items as $pack)
            <tr>
                <td>{{ $pack->id }}</td>
                <td>{{ $pack->product->name_ru }}</td>
                <td>{{ $pack->volume }}</td>
                <td>{{ $pack->price }}</td>
                <td>
                    <a href="{{ route('admin.packagings.edit',$pack) }}" class="btn btn-warning btn-sm">Edit</a>
                    <form action="{{ route('admin.packagings.destroy',$pack) }}" method="POST" class="d-inline">
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
