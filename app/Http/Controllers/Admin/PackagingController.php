<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Http\Requests\Api\Packaging\CreateRequest;
use App\Http\Requests\Api\Packaging\UpdateRequest;
use App\Models\Packaging;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;


class PackagingController extends BaseAdminController
{
    public function index()
    {
        $items = Packaging::with('product')->simplePaginate(15);
        return view('admin.packagings.index', compact('items'));
    }

    public function create()
    {
        return view('admin.packagings.create');
    }

    public function store(CreateRequest $r)
    {
        Packaging::create($r->validated());
        return redirect()->route('admin.packagings.index')->with('success', 'Создано');
    }

    public function edit(Packaging $packaging)
    {
        return view('admin.packagings.edit', compact('packaging'));
    }

    public function update(UpdateRequest $r, Packaging $packaging)
    {
        $packaging->update($r->validated());
        return redirect()->route('admin.packagings.index')->with('success', 'Обновлено');
    }

    public function destroy(Packaging $packaging)
    {
        $packaging->delete();
        return back()->with('success', 'Удалено');
    }
}
