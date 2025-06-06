<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Http\Requests\Api\OrderItem\CreateRequest;
use App\Http\Requests\Api\OrderItem\UpdateRequest;
use App\Models\OrderItem;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;


class OrderItemController extends BaseAdminController
{
    public function index()
    {
        $items = OrderItem::simplePaginate(15);
        return view('admin.order-items.index', compact('items'));
    }

    public function create()
    {
        return view('admin.order-items.create');
    }

    public function store(CreateRequest $r)
    {
        OrderItem::create($r->validated());
        return redirect()->route('admin.order-items.index')->with('success', 'Создано');
    }

    public function edit(OrderItem $orderItem)
    {
        return view('admin.order-items.edit', compact('orderItem'));
    }

    public function update(UpdateRequest $r, OrderItem $orderItem)
    {
        $orderItem->update($r->validated());
        return redirect()->route('admin.order-items.index')->with('success', 'Обновлено');
    }

    public function destroy(OrderItem $orderItem)
    {
        $orderItem->delete();
        return back()->with('success', 'Удалено');
    }
}
