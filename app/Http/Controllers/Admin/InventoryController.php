<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Http\Requests\Api\Inventory\CreateRequest;
use App\Http\Requests\Api\Inventory\UpdateRequest;
use App\Models\Inventory;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;


class InventoryController extends BaseAdminController
{
    public function index()
    {
        $items = Inventory::with(['city', 'district', 'packaging'])->simplePaginate(15);
        return view('admin.inventories.index', compact('items'));
    }

    public function create()
    {
        return view('admin.inventories.create');
    }

    public function store(CreateRequest $r)
    {
        Inventory::create($r->validated());
        return redirect()->route('admin.inventories.index')->with('success', 'Создано');
    }

    public function edit(Inventory $inventory)
    {
        return view('admin.inventories.edit', compact('inventory'));
    }

    public function update(UpdateRequest $r, Inventory $inventory)
    {
        $inventory->update($r->validated());
        return redirect()->route('admin.inventories.index')->with('success', 'Обновлено');
    }

    public function destroy(Inventory $inventory)
    {
        $inventory->delete();
        return back()->with('success', 'Удалено');
    }
}
