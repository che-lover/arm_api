<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;

class BaseAdminController extends Controller
{
    protected string $apiPrefix = '/api/v1';

    /**
     * Вызов API-эндпоинта внутри приложения
     *
     * @param string $method GET|POST|PUT|DELETE
     * @param string $uri    путь после /api/v1
     * @param array  $data   параметры тела или query
     * @return array|null
     */
    protected function callApi(string $method, string $uri, array $data = []): ?array
    {
        $request = Request::create("{$this->apiPrefix}{$uri}", $method, $data);
        $response = app()->handle($request);
        $content  = $response->getContent();

        return json_decode($content, true)['data'] ?? null;
    }
}
