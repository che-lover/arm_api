<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;

Route::get('/user', function (Request $request) {
    return $request->user();
})->middleware('auth:sanctum');

Route::get('/info', \App\Http\Controllers\Api\IndexController::class)->name('info');

Route::group(['prefix' => 'v1'], function () {
    Route::apiResource('cities', \App\Http\Controllers\Api\CityController::class);
    Route::apiResource('districts', \App\Http\Controllers\Api\DistrictController::class);
    Route::apiResource('inventories', \App\Http\Controllers\Api\InventoryController::class);
    Route::apiResource('packagings', \App\Http\Controllers\Api\PackagingController::class);
    Route::apiResource('products', \App\Http\Controllers\Api\ProductController::class);
    Route::apiResource('orders', \App\Http\Controllers\Api\OrderController::class);
    Route::apiResource('coupons', \App\Http\Controllers\Api\CouponController::class);
    Route::apiResource('order-items', \App\Http\Controllers\Api\OrderItemController::class);
});
