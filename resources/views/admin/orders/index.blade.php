@extends('layouts.admin')
@section('content')
    <div class="d-flex justify-content-between mb-3">
        <h1>Orders</h1>
{{--        <a href="{{ route('admin.orders.create') }}" class="btn btn-primary btn-sm">Add Order</a>--}}
    </div>
    <table class="table table-striped">
        <thead><tr><th>#</th><th>User ID</th><th>Total</th><th>Status</th><th>Actions</th></tr></thead>
        <tbody>
        @foreach($items as $order)
            <tr>
                <td>{{ $order->id }}</td>
                <td>{{ $order->user_id }}</td>
                <td>{{ $order->total_amount }}</td>
                <td>{{ $order->status }}</td>
                <td>
                    <a href="{{ route('admin.orders.edit',$order) }}" class="btn btn-warning btn-sm">Edit</a>
                    <form action="{{ route('admin.orders.destroy',$order) }}" method="POST" class="d-inline">
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
