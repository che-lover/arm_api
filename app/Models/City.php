<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class City extends Model
{
    use HasFactory;
    protected $fillable = [
        'name_ru', 'name_en', 'name_hy'
    ];

    public function disctricts()
    {
        return $this->hasMany(District::class);
    }
    public function inventories()
    {
        return $this->hasMany(Inventory::class);
    }
}
