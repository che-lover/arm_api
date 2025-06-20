<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\Api\Inventory\CreateRequest;
use App\Http\Requests\Api\Inventory\UpdateRequest;
use App\Models\Inventory;
use Illuminate\Http\Request;

class InventoryController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(Request $request)
    {
//        $inventories = Inventory::with(['city', 'district', 'packaging'])->get();

        $q = Inventory::with(['city', 'district', 'packaging', 'packaging.product']);

        // какой статус возвращать: по умолчанию 'new'
        $status = $request->query('status', 'confirmed');
        $q->where('status', $status);

        // дополнительная фильтрация (если понадобится)
        if ($request->filled('city_id')) {
            $q->where('city_id', $request->query('city_id'));
        }
        if ($request->filled('district_id')) {
            $q->where('district_id', $request->query('district_id'));
        }

        $inventories = $q->get();

        return response()->json([
            'success' => true,
            'data'    => $inventories,
        ], 200);
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(CreateRequest $request)
    {
        $data = $request->validated();

        $inventory = Inventory::firstOrCreate($data);

        return response()->json(["success" => true, "inventory" => $inventory]);
    }

    /**
     * Display the specified resource.
     */
    public function show(Inventory $inventory)
    {
        $inventory->load(['city', 'district', 'packaging']);

        return response()->json(['success' => true, 'data' => $inventory]);
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(UpdateRequest $request, Inventory $inventory)
    {
        $data = $request->validated();

        $inventory->update($data);

        return response()->json(["success" => true, "inventory" => $inventory]);
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(Inventory $inventory)
    {
        $inventory->delete();

        return response()->noContent();
    }
}
