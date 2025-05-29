<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class District extends Model
{
    use HasFactory;
    protected $fillable = [
        'city_id',
        'name_ru',
        'name_en',
        'name_hy'
    ];

    public function city()
    {
        return $this->belongsTo(City::class);
    }

    public function inventories()
    {
        return $this->hasMany(Inventory::class);
    }
}
