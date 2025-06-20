<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Http\Requests\Api\District\CreateRequest;
use App\Http\Requests\Api\District\UpdateRequest;
use App\Models\District;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;


class DistrictController extends BaseAdminController
{
    public function index()
    {
        $items = District::simplePaginate(15);
        return view('admin.districts.index', compact('items'));
    }

    public function create()
    {
        return view('admin.districts.create');
    }

    public function store(CreateRequest $r)
    {
        District::create($r->validated());
        return redirect()->route('admin.districts.index')->with('success', 'Создано');
    }

    public function edit(District $district)
    {
        return view('admin.districts.edit', compact('district'));
    }

    public function update(UpdateRequest $r, District $district)
    {
        $district->update($r->validated());
        return redirect()->route('admin.districts.index')->with('success', 'Обновлено');
    }

    public function destroy(District $district)
    {
        $district->delete();
        return back()->with('success', 'Удалено');
    }
}
