<?php

namespace App\Http\Requests\Api\District;

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
            "name_ru" => "required|string",
            "name_en" => "required|string",
            "name_hu" => "nullable|string"
        ];
    }
}
