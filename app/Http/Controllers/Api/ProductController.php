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
    public function index(Request $request)
    {
        // читаем параметры из запроса
        $cityId     = $request->query('city_id');
        $districtId = $request->query('district_id');

        // базовый запрос
        $query = Product::query();

        // если пришли и city_id, и district_id — фильтруем
        if ($cityId && $districtId) {
            $query->whereHas('packagings.inventories', function ($q) use ($cityId, $districtId) {
                $q->where('city_id', $cityId)
                    ->where('district_id', $districtId)
                    ->whereNotIn('status', ['sold', 'pending']);
            });
        }

        // подгружаем только упаковки, которые тоже проходят ту же фильтрацию по складам
        $products = $query->with(['packagings' => function ($q) use ($cityId, $districtId) {
            $q->whereHas('inventories', function ($iq) use ($cityId, $districtId) {
                $iq->where('city_id', $cityId)
                    ->where('district_id', $districtId)
                    ->whereNotIn('status', ['sold', 'pending']);
            });
        }])->get();

        return response()->json([
            'success' => true,
            'data'    => $products,
        ], 200);
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
