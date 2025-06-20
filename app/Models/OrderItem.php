<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class OrderItem extends Model
{
    use HasFactory;
    protected $fillable = [
        'order_id', 'packaging_id', 'quantity', 'price', 'inventory_id'
    ];

    public function order() {
        return $this->belongsTo(Order::class);
    }
    public function packaging() {
        return $this->belongsTo(Packaging::class);
    }
    public function inventory() {
        return $this->belongsTo(Inventory::class);
    }
}
