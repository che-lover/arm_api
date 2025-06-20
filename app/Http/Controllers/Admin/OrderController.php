<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Http\Requests\Api\Order\CreateRequest;
use App\Http\Requests\Api\Order\UpdateRequest;
use App\Models\Order;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;


class OrderController extends BaseAdminController
{
    public function index()
    {
        $items = Order::with(['user', 'items'])->simplePaginate(15);
        return view('admin.orders.index', compact('items'));
    }

    public function show(Order $order)
    {
        $order->load(['user', 'items']);
        return view('admin.orders.show', compact('order'));
    }

    public function edit(Order $order)
    {
        return view('admin.orders.edit', compact('order'));
    }

    public function update(UpdateRequest $r, Order $order)
    {
        $order->update($r->validated());
        return redirect()->route('admin.orders.index')->with('success', 'Обновлено');
    }

    public function destroy(Order $order)
    {
        $order->delete();
        return back()->with('success', 'Удалено');
    }
}
