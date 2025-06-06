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
    public function index()
    {
        $packagings = Packaging::all();

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
