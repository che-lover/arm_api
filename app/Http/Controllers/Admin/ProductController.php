<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Http\Requests\Api\Product\CreateRequest;
use App\Http\Requests\Api\Product\UpdateRequest;
use App\Models\Product;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;


class ProductController extends BaseAdminController
{
    public function index()
    {
        $items = Product::simplePaginate(15);
        return view('admin.products.index', compact('items'));
    }

    public function create()
    {
        return view('admin.products.create');
    }

    public function store(CreateRequest $r)
    {
        Product::create($r->validated());
        return redirect()->route('admin.products.index')->with('success', 'Создано');
    }

    public function edit(Product $product)
    {
        return view('admin.products.edit', compact('product'));
    }

    public function update(UpdateRequest $r, Product $product)
    {
        $product->update($r->validated());
        return redirect()->route('admin.products.index')->with('success', 'Обновлено');
    }

    public function destroy(Product $product)
    {
        $product->delete();
        return back()->with('success', 'Удалено');
    }
}
