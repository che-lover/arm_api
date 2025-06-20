<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\Api\City\UpdateRequest;
use App\Http\Requests\Api\District\CreateRequest;
use App\Models\District;
use Illuminate\Http\Request;

class DistrictController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(Request $request)
    {
        $q = District::query();
        if (isset($request->city_id)) {
            $q->where('city_id', $request->city_id)
              ->whereHas('inventories');
        }

        $districts = $q->get();
        $districts->load('city');

        return response()->json(['success' => true, 'data' => $districts]);
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(CreateRequest $request)
    {
        $data = $request->validated();

        $district = District::firstOrCreate($data);

        return response()->json(['success' => true, 'data' => $district]);
    }

    /**
     * Display the specified resource.
     */
    public function show(District $district)
    {
        $district->load('city', 'inventories');

        return response()->json(['success' => true, 'data' => $district]);
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(UpdateRequest $request, District $district)
    {
        $data = $request->validated();

        $district->update($data);

        return response()->json(['success' => true, 'data' => $district]);
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(District $district)
    {
        $district->delete();
    }
}
