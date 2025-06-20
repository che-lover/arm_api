<?php

namespace App\Http\Requests\Api\Inventory;

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
            "city_id" => "required|integer|exists:cities,id",
            "district_id" => "required|integer|exists:districts,id",
            "packaging_id" => "required|integer|exists:packagings,id",
            "quantity" => "required|integer",
            "photo_url" => "nullable|string",
            "status" => "nullable|string",
        ];
    }
}
