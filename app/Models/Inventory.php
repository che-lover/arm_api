<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Inventory extends Model
{
    use HasFactory;
    protected $fillable = [
        'city_id', 'district_id', 'packaging_id', 'quantity', 'photo_url'
    ];

    public function city()
    {
        return $this->belongsTo(City::class);
    }
    public function district() {
        return $this->belongsTo(District::class);
    }
    public function packaging() {
        return $this->belongsTo(Packaging::class);
    }
}
