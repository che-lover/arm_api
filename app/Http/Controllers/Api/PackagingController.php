<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\Api\Packaging\CreateRequest;
use App\Http\Requests\Api\Packaging\UpdateRequest;
use App\Models\Inventory;
use App\Models\Packaging;
use Illuminate\Http\Request;

class PackagingController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(Request $request)
    {
        $query = Packaging::query()
            ->whereHas('inventories', fn($q) => $q->where('quantity', '>', 0))
            ->when($request->filled('city_id'), fn($q) =>
            $q->whereHas('inventories', fn($q) =>
            $q->where('city_id', $request->city_id)
            )
            )
            ->when($request->filled('district_id'), fn($q) =>
            $q->whereHas('inventories', fn($q) =>
            $q->where('district_id', $request->district_id)
            )
            )
            // вот это добавляем
            ->when($request->filled('product_id'), fn($q) =>
            $q->where('product_id', $request->product_id)
            );

        $packagings = $query->with(['product', 'inventories'])->get();

        return response()->json(['success' => true, 'data' => $packagings]);
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(CreateRequest $request)
    {
        $data = $request->validated();

        $packaging = Packaging::firstOrCreate($data);

        return response()->json(['success' => true, 'data' => $packaging]);
    }

    /**
     * Display the specified resource.
     */
    public function show(Packaging $packaging)
    {
        $packaging->load('product', 'inventories');

        return response()->json(['success' => true, 'data' => $packaging]);
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(UpdateRequest $request, Packaging $packaging)
    {
        $data = $request->validated();

        $packaging->update($data);

        return response()->json(['success' => true, 'data' => $packaging]);
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(Packaging $packaging)
    {
        $packaging->delete();
        return response()->noContent();
    }
}
