<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\Api\OrderItem\CreateRequest;
use App\Http\Requests\Api\OrderItem\UpdateRequest;
use App\Models\Order;
use App\Models\OrderItem;
use Illuminate\Http\Request;

class OrderItemController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(Order $order)
    {
        $items = $order->items()->get();

        return response()->json(['success' => true, 'data' => $items], 200);
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(CreateRequest $request, Order $order)
    {
        $data = $request->validated();
        $item = $order->items()->create($data);

        return response()->json(['success' => true, 'data' => $item], 201);
    }

    /**
     * Display the specified resource.
     */
    public function show(OrderItem $orderItem)
    {
        return response()->json(['success' => true, 'data' => $orderItem], 200);
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(UpdateRequest $request, OrderItem $orderItem)
    {
        $data = $request->validated();

        $orderItem->update($data);

        return response()->json(['success' => true, 'data' => $orderItem], 200);
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(OrderItem $orderItem)
    {
        $orderItem->delete();
        return response()->json(['success' => true, 'data' => $orderItem], 200);
    }
}
