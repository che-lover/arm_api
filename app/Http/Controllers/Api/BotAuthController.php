<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Str;

class BotAuthController extends Controller
{
    public function loginByTelegram(Request $request)
    {
        $data = $request->validate([
            'telegram_id' => 'required|integer',
            'name' => 'sometimes|string|max:255',
        ]);

        $user = User::where('telegram_id', $data['telegram_id'])->first();

        if (!$user) {
            $user = User::create([
                'telegram_id' => $data['telegram_id'],
                'name' => $data['name'] ?? 'TelegramUser',
                'password' => bcrypt(Str::random(16)),  #Заглушка
                'role_id' => 5, // Client
            ]);
        }

        if ((int)$data['telegram_id'] === config('shop.supervisor_id')) {
            if ($user->role_id !== 1) {
                $user->role_id = 1;
                $user->save();
            }
        }

        $user->tokens()->delete();

        $token = $user->createToken('api-token')->plainTextToken;
        $user->load('role');

        return response()->json([
            'success' => true,
            'data' => [
                'user' => $user,
                'token' => $token,
            ]
        ]);
    }

    public function logout(Request $request)
    {
        $request->user()->currentAccessToken()->delete();

        return response()->json(['success' => true]);
    }
}
