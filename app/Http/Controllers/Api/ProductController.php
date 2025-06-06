<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\Api\Product\CreateRequest;
use App\Http\Requests\Api\Product\UpdateRequest;
use App\Models\Product;
use Illuminate\Http\Request;

class ProductController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        $products = Product::all();

        return response()->json(['success' => true, 'data' => $products]);
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(CreateRequest $request)
    {
        $data = $request->validated();

        $product = Product::firstOrCreate($data);

        return response()->json(['success' => true, 'data' => $product]);
    }

    /**
     * Display the specified resource.
     */
    public function show(Product $product)
    {
        $product->load('packagings');

        return response()->json(['success' => true, 'data' => $product]);
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(UpdateRequest $request, Product $product)
    {
        $data = $request->validated();

        $product->update($data);

        return response()->json(['success' => true, 'data' => $product]);
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(Product $product)
    {
        $id = $product->id;
        $product->delete();

        return response()->json(['success' => true, 'data' => ["product with id $id deleted"]]);
    }
}
