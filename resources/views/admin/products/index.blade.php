@extends('layouts.admin')
@section('content')
    <div class="d-flex justify-content-between mb-3">
        <h1>Products</h1>
        <a href="{{ route('admin.products.create') }}" class="btn btn-primary btn-sm">Add Product</a>
    </div>
    <table class="table table-striped">
        <thead><tr><th>#</th><th>Name RU</th><th>Name EN</th><th>Name HY</th><th>Actions</th></tr></thead>
        <tbody>
        @foreach($items as $product)
            <tr>
                <td>{{ $product->id }}</td>
                <td>{{ $product->name_ru }}</td>
                <td>{{ $product->name_en }}</td>
                <td>{{ $product->name_hy }}</td>
                <td>
                    <a href="{{ route('admin.products.edit',$product) }}" class="btn btn-warning btn-sm">Edit</a>
                    <form action="{{ route('admin.products.destroy',$product) }}" method="POST" class="d-inline">
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
