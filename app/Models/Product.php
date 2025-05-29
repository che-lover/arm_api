<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Product extends Model
{
    use HasFactory;
    protected $fillable = [
        'name_ru', 'name_en', 'name_hy',
        'description_ru', 'description_en', 'description_hy',
    ];

    public function packagings()
    {
        return $this->hasMany(Packaging::class);
    }
}
