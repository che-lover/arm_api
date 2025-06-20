<?php

namespace Database\Factories;

use App\Models\City;
use App\Models\District;
use App\Models\Order;
use App\Models\User;
use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends \Illuminate\Database\Eloquent\Factories\Factory<\App\Models\Order>
 */
class OrderFactory extends Factory
{
    protected $model = Order::class;
    /**
     * Define the model's default state.
     *
     * @return array<string, mixed>
     */
    public function definition(): array
    {
        return [
            'user_id' => User::factory(),
            'city_id' => City::factory(),
            'district_id' => District::factory(),
            'total_amount' => $this->faker->randomFloat(2, 1, 1000),
            'status' => $this->faker->word(),
        ];
    }
}
