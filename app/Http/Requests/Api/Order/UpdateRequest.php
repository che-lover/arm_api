<?php

namespace App\Http\Requests\Api\Order;

use Illuminate\Foundation\Http\FormRequest;

class UpdateRequest extends FormRequest
{
    /**
     * Determine if the user is authorized to make this request.
     */
    public function authorize(): bool
    {
        return true;
    }

    /**
     * Get the validation rules that apply to the request.
     *
     * @return array<string, \Illuminate\Contracts\Validation\ValidationRule|array<mixed>|string>
     */
    public function rules(): array
    {
        return [
            "user_id" => "nullable|int|exists:users,id",
            "city_id" => "nullable|int|exists:cities,id",
            "district_id" => "nullable|int|exists:districts,id",
            "total_amount" => "nullable|int|decimal",
            "status" => "nullable|string",
            "coupon_id" => "nullable|int|exists:coupons,id",
        ];
    }
}
