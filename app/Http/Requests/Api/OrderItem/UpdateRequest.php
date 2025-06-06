<?php

namespace App\Http\Requests\Api\OrderItem;

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
            "order_id" => "nullable|int|exists:orders,id",
            "packaging_id" => "nullable|int|exists:packagings,id",
            "quantity" => "nullable|int",
            "price" => "nullable|int",
        ];
    }
}
