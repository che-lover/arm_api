<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\Api\OrderItem\CreateRequest;
use App\Http\Requests\Api\OrderItem\UpdateRequest;
use App\Models\Inventory;
use App\Models\Order;
use App\Models\OrderItem;
use App\Models\Packaging;
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
    public function store(CreateRequest $request)
    {

        $data  = $request->validated();
        $order = Order::findOrFail($data['order_id']);


        $inventory = Inventory::where('packaging_id', $data['packaging_id'])
            ->where('city_id',     $order->city_id)
            ->where('district_id', $order->district_id)
            ->where('status',      'confirmed')         // или 'confirmed'
            ->where('quantity',   '>=', $data['quantity'])
            ->firstOrFail();

        $item = $order->items()->create([
            'packaging_id' => $data['packaging_id'],
            'quantity'     => $data['quantity'],
            'price'        => $inventory->packaging->price,
            'inventory_id' => $inventory->id,
        ]);
        $item->load('packaging');

        return response()->json([
            'success' => true,
            'data'    => $item,
        ], 201);
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
