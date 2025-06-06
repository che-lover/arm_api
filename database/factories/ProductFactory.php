<?php

namespace Database\Factories;

use App\Models\Product;
use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends \Illuminate\Database\Eloquent\Factories\Factory<\App\Models\Product>
 */
class ProductFactory extends Factory
{
    protected $model = Product::class;
    /**
     * Define the model's default state.
     *
     * @return array<string, mixed>
     */
    public function definition(): array
    {
        return [
            'name_ru' => $this->faker->name . ' ru',
            'name_en' => $this->faker->name . ' en',
            'name_hy' => $this->faker->name . ' hy',
            'description_ru' => $this->faker->text,
            'description_en' => $this->faker->text,
            'description_hy' => $this->faker->text,
        ];
    }
}
