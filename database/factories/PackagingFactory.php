<?php

namespace Database\Factories;

use App\Models\Packaging;
use App\Models\Product;
use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends \Illuminate\Database\Eloquent\Factories\Factory<\App\Models\Packaging>
 */
class PackagingFactory extends Factory
{
    protected $model = Packaging::class;
    /**
     * Define the model's default state.
     *
     * @return array<string, mixed>
     */
    public function definition(): array
    {
        return [
            'product_id' => Product::factory(),
            'volume' => $this->faker->randomElement([100, 500, 1000]),
            'price' => $this->faker->randomFloat(2, 1, 100),
        ];
    }
}
