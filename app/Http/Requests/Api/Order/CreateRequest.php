<?php

namespace App\Http\Requests\Api\Order;

use Illuminate\Foundation\Http\FormRequest;

class CreateRequest extends FormRequest
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
            "city_id" => "required|int|exists:cities,id",
            "district_id" => "required|int|exists:districts,id",
            "total_amount" => "nullable|numeric",
            "status" => "nullable|string",
            "coupon_id" => "nullable|int|exists:coupons,id",
        ];
    }
}
