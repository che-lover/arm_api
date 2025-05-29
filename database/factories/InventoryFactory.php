<?php

namespace Database\Factories;

use App\Models\City;
use App\Models\District;
use App\Models\Inventory;
use App\Models\Packaging;
use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends \Illuminate\Database\Eloquent\Factories\Factory<\App\Models\Inventory>
 */
class InventoryFactory extends Factory
{
    protected $model = Inventory::class;
    /**
     * Define the model's default state.
     *
     * @return array<string, mixed>
     */
    public function definition(): array
    {
        return [
            'city_id' => City::factory(),
            'district_id' => District::factory(),
            'packaging_id' => Packaging::factory(),
            'quantity' => $this->faker->numberBetween(1, 50),
            'photo_url' => $this->faker->imageUrl(640, 480),
        ];
    }
}
