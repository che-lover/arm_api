<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Requests\Api\City\CreateRequest;
use App\Http\Requests\Api\City\UpdateRequest;
use App\Models\City;

class CityController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        return response()->json(City::paginate(10));
    }

    /**
     * Show the form for creating a new resource.
     */
    public function create()
    {

    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(CreateRequest $request)
    {
        $data = $request->validated();

        $city = City::firstOrCreate($data);

        return response()->json(["success" => true, "city" => $city]);
    }

    /**
     * Display the specified resource.
     */
    public function show(City $city)
    {
        $city->load('disctricts', 'inventories');

        return response()->json(["success" => true, "city" => $city]);
    }

    /**
     * Show the form for editing the specified resource.
     */
    public function edit(City $city)
    {
        //
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(UpdateRequest $request, City $city)
    {
        $data = $request->validated();

        $city->update($data);

        return response()->json(["success" => true, "city" => $city]);
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(City $city)
    {
        $city->delete();
    }
}
