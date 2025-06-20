<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\Api\Order\CreateRequest;
use App\Http\Requests\Api\Order\UpdateRequest;
use App\Models\Coupon;
use App\Models\Order;
use Illuminate\Http\Request;

class OrderController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        $orders = Order::with(['user', 'city', 'district', 'coupon', 'items'])->get();

        return response()->json(['success' => true, 'data' => $orders], 200);
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(CreateRequest $request)
    {
//        dd(111);
//        dd(1);
        $user = $request->user();

        $data = $request->validated();

        if(!empty($data['coupon_id'])) {
            $coupon = Coupon::findOrFail($data['coupon_id']);
            if ($coupon->used || ($coupon->expires_at && $coupon->expires_at->isPast())) {
                return response()->json(['success' => false, 'error' => 'Invalid or expired coupon'], 400);
            }
        }

        $order = Order::create([
            'user_id' => $user->id,
            'city_id' => $data['city_id'],
            'district_id' => $data['district_id'],
            'total_amount' => 10,
            'status' => 'new',
            'coupon_id' => $data['coupon_id'] ?? null,
        ]);

        return response()->json(['success' => true, 'data' => $order], 201);
    }

    /**
     * Display the specified resource.
     */
    public function show(Order $order)
    {
        $order->load(['user', 'city', 'district', 'coupon', 'items']);

        return response()->json(['success' => true, 'data' => $order], 200);
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(UpdateRequest $request, Order $order)
    {
        $data = $request->validated();

        $order->update($data);

        return response()->json(['success' => true, 'data' => $order], 200);
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(Order $order)
    {
        $order->delete();

        return response()->noContent();
    }
}
