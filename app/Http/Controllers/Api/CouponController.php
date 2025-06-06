<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\Api\Coupon\CreateRequest;
use App\Http\Requests\Api\Coupon\UpdateRequest;
use App\Models\Coupon;
use Illuminate\Http\Request;

class CouponController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        $coupons = Coupon::all();

        return response()->json(['success' => true, 'data' => $coupons], 200);
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(CreateRequest $request)
    {
        $data = $request->validated();

        $coupon = Coupon::create($data);

        return response()->json(['success' => true, 'data' => $coupon], 201);
    }

    /**
     * Display the specified resource.
     */
    public function show(Coupon $coupon)
    {
        return response()->json(['success' => true, 'data' => $coupon], 200);
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(UpdateRequest $request, Coupon $coupon)
    {
        $data = $request->validated();

        $coupon->update($data);

        return response()->json(['success' => true, 'data' => $coupon], 200);
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(Coupon $coupon)
    {
        $coupon->delete();

        return response()->noContent();
    }
}
