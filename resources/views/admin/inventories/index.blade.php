@extends('layouts.admin')
@section('content')
    <div class="d-flex justify-content-between mb-3">
        <h1>Inventory</h1>
        <a href="{{ route('admin.inventories.create') }}" class="btn btn-primary btn-sm">Add Inventory</a>
    </div>
    <table class="table table-striped">
        <thead><tr><th>#</th><th>City</th><th>District</th><th>Packaging vol</th><th>Product</th><th>Status</th><th>Quantity</th><th>Photo URL</th><th>Actions</th></tr></thead>
        <tbody>
        @foreach($items as $inv)
            <tr>
                <td>{{ $inv->id }}</td>
                <td>{{ $inv->city->name_ru }}</td>
                <td>{{ $inv->district->name_ru }}</td>
                <td>{{ $inv->packaging->volume . '(id ' . $inv->packaging->id . ' )' }}</td>
                <td>{{ $inv->packaging->product->id . '( ' . $inv->packaging->product->name_ru . ' )' }}</td>
                <td>{{ $inv->status }}</td>
                <td>{{ $inv->quantity }}</td>
                <td><a href="{{ $inv->photo_url }}" target="_blank">View</a></td>
                <td>
                    <a href="{{ route('admin.inventories.edit',$inv) }}" class="btn btn-warning btn-sm">Edit</a>
                    <form action="{{ route('admin.inventories.destroy',$inv) }}" method="POST" class="d-inline">
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
