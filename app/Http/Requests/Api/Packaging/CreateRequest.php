<?php

namespace App\Http\Requests\Api\Packaging;

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
            "product_id" => "required|int|exists:products,id",
            "volume" => "required|int|between:1,100",
            "price" => "required|numeric",
        ];
    }
}
