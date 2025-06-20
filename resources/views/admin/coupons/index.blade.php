@extends('layouts.admin')
@section('content')
    <div class="d-flex justify-content-between mb-3">
        <h1>Coupons</h1>
        <a href="{{ route('admin.coupons.create') }}" class="btn btn-primary btn-sm">Add Coupon</a>
    </div>
    <table class="table table-striped">
        <thead><tr><th>#</th><th>Code</th><th>Discount</th><th>Expires At</th><th>Used</th><th>Actions</th></tr></thead>
        <tbody>
        @foreach($items as $coupon)
            <tr>
                <td>{{ $coupon->id }}</td>
                <td>{{ $coupon->code }}</td>
                <td>{{ $coupon->discount_amount }}</td>
                <td>{{ $coupon->expires_at }}</td>
                <td>{{ $coupon->used ? 'Yes' : 'No' }}</td>
                <td>
                    <a href="{{ route('admin.coupons.edit',$coupon) }}" class="btn btn-warning btn-sm">Edit</a>
                    <form action="{{ route('admin.coupons.destroy',$coupon) }}" method="POST" class="d-inline">
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
