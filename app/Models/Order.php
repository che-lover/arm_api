<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Order extends Model
{
    use HasFactory;
    protected $fillable = [
        'user_id', 'city_id', 'district_id',
        'total_amount', 'status', 'coupon_id',
        'payment_address', 'amount_dash', 'paid_at'
    ];

    public function user() {
        return $this->belongsTo(User::class);
    }
    public function city() {
        return $this->belongsTo(City::class);
    }
    public function district() {
        return $this->belongsTo(District::class);
    }
    public function coupon() {
        return $this->belongsTo(Coupon::class);
    }
    public function items() {
        return $this->hasMany(OrderItem::class);
    }
}
