<?php

use Illuminate\Support\Facades\Route;

//Route::get('/', function () {
//    return view('index');
//});

Route::group(['prefix' => '/admin'], function () {
    Route::get('/', function () {
        return redirect()->route('admin.cities.index');
    });
    Route::resource('cities', \App\Http\Controllers\Admin\CityController::class)->names('admin.cities');
    Route::resource('coupons', \App\Http\Controllers\Admin\CouponController::class)->names('admin.coupons');
    Route::resource('districts', \App\Http\Controllers\Admin\DistrictController::class)->names('admin.districts');
    Route::resource('inventories', \App\Http\Controllers\Admin\InventoryController::class)->names('admin.inventories');
    Route::resource('orders', \App\Http\Controllers\Admin\OrderController::class)->names('admin.orders');
    Route::resource('order-items', \App\Http\Controllers\Admin\OrderItemController::class)->names('admin.order-items');
    Route::resource('packagings', \App\Http\Controllers\Admin\PackagingController::class)->names('admin.packagings');
    Route::resource('products', \App\Http\Controllers\Admin\ProductController::class)->names('admin.products');
});

Route::get('/phpinfo', fn() => phpinfo());
