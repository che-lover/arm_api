<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;

Route::get('/user', function (Request $request) {
    return $request->user();
})->middleware('auth:sanctum');
/*
|--------------------------------------------------------------------------
| API Routes
|--------------------------------------------------------------------------
|
| Здесь мы описываем публичные маршруты для Telegram-бота (логин по telegram_id)
| и саму версию API v1 с разграничением прав через auth:sanctum + role:…
|
*/

// --------------------
// 1) «Проверка текущего user» (через Sanctum)
Route::get('/user', function (Request $request) {
    return $request->user();
})->middleware('auth:sanctum');


// --------------------


// --------------------
// 3) Публичная информация (без авторизации)
//    — возвращаем любой JSON, например, версия API или что-то общее
Route::get('/info', [\App\Http\Controllers\Api\IndexController::class, '__invoke'])
    ->name('info');


// --------------------
// 4) Версия 1 API (v1/*)
//    Мы разбиваем на разные группы:
//    — «просмотр» (index & show) без авторизации
//    — «изменение» (store/update/destroy) под разными ролями
Route::prefix('v1')->group(function () {
    // 2) Sanctum login/logout (по Telegram-ID)
    Route::post('auth/bot-login', [\App\Http\Controllers\Api\BotAuthController::class, 'loginByTelegram']);
    Route::post('auth/bot-logout', [\App\Http\Controllers\Api\BotAuthController::class, 'logout'])
        ->middleware('auth:sanctum');

    /*
    |------------------------------------------------------------------------
    | 4.1. ГОРОДА (cities)
    |  - Любой может посмотреть (GET index, GET show) — без auth
    |  - Создавать/редактировать/удалять может только manager или admin
    |------------------------------------------------------------------------
    */
    Route::apiResource('cities', \App\Http\Controllers\Api\CityController::class)
        ->only(['index', 'show']); // публичные методы

    Route::middleware(['auth:sanctum', 'role:supervisor,manager,admin'])->group(function () {
        Route::post('cities', [\App\Http\Controllers\Api\CityController::class, 'store']);
        Route::put('cities/{city}', [\App\Http\Controllers\Api\CityController::class, 'update']);
        Route::delete('cities/{city}', [\App\Http\Controllers\Api\CityController::class, 'destroy']);
    });


    /*
    |------------------------------------------------------------------------
    | 4.2. РАЙОНЫ (districts)
    |  - Любой может посмотреть список и детали — без auth
    |  - Создавать/редактировать/удалять может только manager или admin
    |------------------------------------------------------------------------
    */
    Route::apiResource('districts', \App\Http\Controllers\Api\DistrictController::class)
        ->only(['index', 'show']);

    Route::middleware(['auth:sanctum', 'role:supervisor,manager,admin'])->group(function () {
        Route::post('districts', [\App\Http\Controllers\Api\DistrictController::class, 'store']);
        Route::put('districts/{district}', [\App\Http\Controllers\Api\DistrictController::class, 'update']);
        Route::delete('districts/{district}', [\App\Http\Controllers\Api\DistrictController::class, 'destroy']);
    });


    /*
    |------------------------------------------------------------------------
    | 4.3. СКЛАДЫ / КЛАДЫ (inventories)
    |  - Любой может посмотреть (index, show) — без auth
    |  - Курьер (role=courier) может создавать (заливать клад) и обновлять (подтверждать/сбрасывать)
    |  - Менеджер/админ (role=manager,admin) тоже могут всё CRUD
    |------------------------------------------------------------------------
    */
    Route::apiResource('inventories', \App\Http\Controllers\Api\InventoryController::class)
        ->only(['index', 'show']);

    

    // Менеджер и Админ: также могут CRUD
    Route::middleware(['auth:sanctum', 'role:supervisor,manager,admin,courier'])->group(function () {
        Route::post('inventories', [\App\Http\Controllers\Api\InventoryController::class, 'store']);
        Route::put('inventories/{inventory}', [\App\Http\Controllers\Api\InventoryController::class, 'update']);
        Route::delete('inventories/{inventory}', [\App\Http\Controllers\Api\InventoryController::class, 'destroy']);
    });


    /*
    |------------------------------------------------------------------------
    | 4.4. ФАСОВКИ (packagings)
    |  - Любой может посмотреть (index, show) — без auth
    |  - Создавать/редактировать/удалять может manager или admin
    |------------------------------------------------------------------------
    */
    Route::apiResource('packagings', \App\Http\Controllers\Api\PackagingController::class)
        ->only(['index', 'show']);

    Route::middleware(['auth:sanctum', 'role:supervisor,manager,admin'])->group(function () {
        Route::post('packagings', [\App\Http\Controllers\Api\PackagingController::class, 'store']);
        Route::put('packagings/{packaging}', [\App\Http\Controllers\Api\PackagingController::class, 'update']);
        Route::delete('packagings/{packaging}', [\App\Http\Controllers\Api\PackagingController::class, 'destroy']);
    });


    /*
    |------------------------------------------------------------------------
    | 4.5. ТОВАРЫ (products)
    |  - Любой может посмотреть (index, show) — без auth
    |  - Создавать/редактировать/удалять может manager или admin
    |------------------------------------------------------------------------
    */
    Route::apiResource('products', \App\Http\Controllers\Api\ProductController::class)
        ->only(['index', 'show']);

    Route::middleware(['auth:sanctum', 'role:supervisor,manager,admin'])->group(function () {
        Route::post('products', [\App\Http\Controllers\Api\ProductController::class, 'store']);
        Route::put('products/{product}', [\App\Http\Controllers\Api\ProductController::class, 'update']);
        Route::delete('products/{product}', [\App\Http\Controllers\Api\ProductController::class, 'destroy']);
    });


    /*
    |------------------------------------------------------------------------
    | 4.6. КУПОНЫ (coupons)
    |  - Любой может посмотреть (index, show) — без auth
    |  - Создавать/редактировать/удалять может manager или admin
    |------------------------------------------------------------------------
    */
    Route::apiResource('coupons', \App\Http\Controllers\Api\CouponController::class)
        ->only(['index', 'show']);

    Route::middleware(['auth:sanctum', 'role:supervisor,manager,admin'])->group(function () {
        Route::post('coupons', [\App\Http\Controllers\Api\CouponController::class, 'store']);
        Route::put('coupons/{coupon}', [\App\Http\Controllers\Api\CouponController::class, 'update']);
        Route::delete('coupons/{coupon}', [\App\Http\Controllers\Api\CouponController::class, 'destroy']);
    });


    /*
    |------------------------------------------------------------------------
    | 4.7. ЗАКАЗЫ (orders)
    |  - Клиент (role=client) может создавать новый заказ (store) и просматривать свои заказ (show)
    |  - Manager/Admin могут смотреть список всех заказов (index), обновлять/удалять (update, destroy)
    |------------------------------------------------------------------------
    */
    // Клиентский доступ: only store + show
    Route::middleware(['auth:sanctum', 'role:client,admin,supervisor'])->group(function () {
        Route::post('orders', [\App\Http\Controllers\Api\OrderController::class, 'store']);
        Route::get('orders/{order}', [\App\Http\Controllers\Api\OrderController::class, 'show']);
    });

    // Manager/Admin: index, update, destroy
    Route::apiResource('orders', \App\Http\Controllers\Api\OrderController::class)
        ->only(['index', 'update', 'destroy']);

    Route::middleware(['auth:sanctum', 'role:supervisor,manager,admin'])->group(function () {
        Route::get('orders', [\App\Http\Controllers\Api\OrderController::class, 'index']);
        Route::put('orders/{order}', [\App\Http\Controllers\Api\OrderController::class, 'update']);
        Route::delete('orders/{order}', [\App\Http\Controllers\Api\OrderController::class, 'destroy']);
    });


    /*
    |------------------------------------------------------------------------
    | 4.8. ПОЗИЦИИ ЗАКАЗА (order-items)
    |  - Клиент (role=client) может добавлять свою позицию в заказ (store) и смотреть детали (show)
    |  - Manager/Admin могут просматривать все позиции (index), обновлять/удалять (update, destroy)
    |------------------------------------------------------------------------
    */
    // Клиентский доступ: store + show
    Route::middleware(['auth:sanctum', 'role:client,admin,supervisor'])->group(function () {
        Route::post('order-items', [\App\Http\Controllers\Api\OrderItemController::class, 'store']);
        Route::get('order-items/{order_item}', [\App\Http\Controllers\Api\OrderItemController::class, 'show']);
    });

    // Manager/Admin: index, update, destroy
    Route::apiResource('order-items', \App\Http\Controllers\Api\OrderItemController::class)
        ->only(['index', 'update', 'destroy']);

    Route::middleware(['auth:sanctum', 'role:supervisor,manager,admin'])->group(function () {
        Route::get('order-items', [\App\Http\Controllers\Api\OrderItemController::class, 'index']);
        Route::put('order-items/{order_item}', [\App\Http\Controllers\Api\OrderItemController::class, 'update']);
        Route::delete('order-items/{order_item}', [\App\Http\Controllers\Api\OrderItemController::class, 'destroy']);
    });

    Route::prefix('payments')->group(function () {
        Route::post('create', [\App\Http\Controllers\Api\PaymentController::class, 'create']);
        Route::get('status/{order}', [\App\Http\Controllers\Api\PaymentController::class, 'status']);
        Route::get('balance', [\App\Http\Controllers\Api\PaymentController::class, 'balance']);
        Route::post('send', [\App\Http\Controllers\Api\PaymentController::class, 'send']);
    });
    
    Route::get('settings/bot',   [\App\Http\Controllers\Api\BotSettingsController::class, 'index']);
    Route::put('settings/bot',   [\App\Http\Controllers\Api\BotSettingsController::class, 'update']);

});

Route::prefix('v1')->middleware(['auth:sanctum','role:supervisor,admin'])->group(function () {
    // 1) Получить список всех пользователей
    //    GET /api/v1/users
    //    Ответ: { success: true, data: [ { id, telegram_id, name, role: { id,name } }, … ] }
    Route::get('users', [\App\Http\Controllers\Api\UserController::class, 'index']);
    
    Route::put('users', [\App\Http\Controllers\Api\UserController::class, 'update']);

    // 2) Получить конкретного пользователя по ID
    //    GET /api/v1/users/{user}
    //    Ответ: { success: true, data: { id, telegram_id, name, role } }
    Route::get('users/{user}', [\App\Http\Controllers\Api\UserController::class, 'show']);

    // 3) Назначить пользователю роль «admin»
    //    POST /api/v1/users/{user}/assign-admin
    //    (без тела — контроллер сам выставит role_id = ID админа)
    //    Ответ: { success: true, data: { …обновлённый пользователь… } }
    Route::post('users/{user}/assign-admin', [\App\Http\Controllers\Api\UserController::class, 'assignAdmin']);

    // 4) Отобрать у пользователя роль «admin» (возвращаем, например, в «client»)
    //    POST /api/v1/users/{user}/revoke-admin
    //    Ответ: { success: true, data: { …обновлённый пользователь… } }
    Route::post('users/{user}/revoke-admin', [\App\Http\Controllers\Api\UserController::class, 'revokeAdmin']);
});
