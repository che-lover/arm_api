<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\BotSetting;
use Illuminate\Http\Request;

class BotSettingsController extends Controller
{
    public function index()
    {
        $settings = BotSetting::firstOrFail();
        return response()->json([
            'success' => true,
            'data'    => $settings,
        ], 200);
    }

    public function update(Request $request)
    {
        $data = $request->validate([
            'exchange_url'      => 'nullable|url',
            'captcha_enabled'   => 'nullable|boolean',
            'channel_link'      => 'nullable|url',
            'operator_contact'  => 'nullable|string',
            'bots'              => 'nullable|array',
        ]);

        $settings = BotSetting::first();
        if (! $settings) {
            $settings = BotSetting::create($data);
        } else {
            $settings->update($data);
        }

        return response()->json([
            'success' => true,
            'data'    => $settings,
        ], 200);
    }
}