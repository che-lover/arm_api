<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Http\Requests\Api\City\CreateRequest;
use App\Http\Requests\Api\City\UpdateRequest;
use App\Models\City;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;


class CityController extends BaseAdminController
{
    // Список
    public function index()
    {
        // simplePaginate убирает SVG и номера страниц
        $cities = City::simplePaginate(15);
        return view('admin.cities.index', compact('cities'));
    }

    public function create()
    {
        return view('admin.cities.create');
    }

    public function store(CreateRequest $request)
    {
        City::create($request->validated());
        return redirect()->route('admin.cities.index')
            ->with('success', 'City created.');
    }

    public function edit(City $city)
    {
        return view('admin.cities.edit', compact('city'));
    }

    public function update(UpdateRequest $request, City $city)
    {
        $city->update($request->validated());
        return redirect()->route('admin.cities.index')
            ->with('success', 'City updated.');
    }

    public function destroy(City $city)
    {
        $city->delete();
        return back()->with('success', 'City deleted.');
    }
}
