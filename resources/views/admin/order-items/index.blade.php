@extends('layouts.admin')
@section('content')
    <div class="d-flex justify-content-between mb-3">
        <h1>Order Items</h1>
        <a href="{{ route('admin.order-items.create') }}" class="btn btn-primary btn-sm">Add Item</a>
    </div>
    <table class="table table-striped">
        <thead><tr><th>#</th><th>Order ID</th><th>Packaging ID</th><th>Quantity</th><th>Price</th><th>Actions</th></tr></thead>
        <tbody>
        @foreach($items as $item)
            <tr>
                <td>{{ $item->id }}</td>
                <td>{{ $item->order_id }}</td>
                <td>{{ $item->packaging_id }}</td>
                <td>{{ $item->quantity }}</td>
                <td>{{ $item->price }}</td>
                <td>
                    <a href="{{ route('admin.order-items.edit',$item) }}" class="btn btn-warning btn-sm">Edit</a>
                    <form action="{{ route('admin.order-items.destroy',$item) }}" method="POST" class="d-inline">
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
