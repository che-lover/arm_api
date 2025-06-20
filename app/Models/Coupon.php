<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Coupon extends Model
{
    use HasFactory;
    protected $fillable = [
        'code', 'discount_amount', 'expires_at', 'used'
    ];
    
    protected $casts = [
        'expires_at' => 'datetime',
        'used'       => 'boolean',
    ];

    public function orders()
    {
        return $this->hasMany(Order::class);
    }
}
