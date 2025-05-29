<?php

namespace Database\Seeders;

use App\Models\City;
use App\Models\Coupon;
use App\Models\District;
use App\Models\Inventory;
use App\Models\Order;
use App\Models\OrderItem;
use App\Models\Packaging;
use App\Models\Product;
use App\Models\User;
// use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    /**
     * Seed the application's database.
     */
    public function run(): void
    {
        // User::factory(10)->create();

//        User::factory()->create([
//            'name' => 'Test User',
//            'email' => 'test@example.com',
//        ]);

        City::factory(5)->create()->each(function (City $city) {
            District::factory(3)->create(['city_id' => $city->id]);
        });

        Product::factory(10)->create()->each(function (Product $product) {
            Packaging::factory(2)->create(['product_id' => $product->id]);
        });

        Inventory::factory(20)->create();
        Coupon::factory(5)->create();

        Order::factory(10)->create()->each(function (Order $order) {
            OrderItem::factory(3)->create(['order_id' => $order->id]);
        });
    }
}
