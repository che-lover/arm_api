<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Http\Requests\Api\Coupon\CreateRequest;
use App\Http\Requests\Api\Coupon\UpdateRequest;
use App\Models\Coupon;
use Illuminate\Http\Request;

class CouponController extends Controller
{
    public function index()
    {
        $items = Coupon::simplePaginate(15);
        return view('admin.coupons.index', compact('items'));
    }

    public function create()
    {
        return view('admin.coupons.create');
    }

    public function store(CreateRequest $r)
    {
        Coupon::create($r->validated());
        return redirect()->route('admin.coupons.index')->with('success', 'Создано');
    }

    public function edit(Coupon $coupon)
    {
        return view('admin.coupons.edit', compact('coupon'));
    }

    public function update(UpdateRequest $r, Coupon $coupon)
    {
        $coupon->update($r->validated());
        return redirect()->route('admin.coupons.index')->with('success', 'Обновлено');
    }

    public function destroy(Coupon $coupon)
    {
        $coupon->delete();
        return back()->with('success', 'Удалено');
    }
}
