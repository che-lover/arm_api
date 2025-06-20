<?php

namespace App\Http\Requests\Api\Inventory;

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
            "city_id" => "nullable|integer|exists:cities,id",
            "district_id" => "nullable|integer|exists:districts,id",
            "packaging_id" => "nullable|integer|exists:packagings,id",
            "quantity" => "nullable|integer",
            "photo_url" => "nullable|string",
            "status" => "nullable|string"
        ];
    }
}
