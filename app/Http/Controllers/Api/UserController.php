<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Models\User;
use App\Models\Role;
use Illuminate\Support\Str;
use Illuminate\Support\Facades\Hash;

class UserController extends Controller
{
    public function index(Request $request)
    {
        if ($request->filled('telegram_id')) {
            $tg = $request->query('telegram_id');
            // firstOrCreate: если нет — создаём сразу
            $user = User::firstOrCreate(
                ['telegram_id' => $tg],
                ['role_id'     => 5,
                  'password' => Hash::make(Str::random(12)),
                  'name' => 'tele_user'
                  ],
            );
            $user->load('role');
            $users = User::with('role')->get();
            return response()->json(['success' => true, 'data' => $users], 200);
        }

        // обычный список всех
        $users = User::with('role')->get();
        return response()->json(['success'=>true, 'data'=>$users], 200);
    }

    public function show(User $user)
    {
        $user->load('role');
        return response()->json(['success'=>true, 'data'=>$user]);
    }

    public function assignAdmin(User $user)
    {
        // допустим, роль admin имеет ID = 2
        $user->role_id = Role::where('name','admin')->first()->id;
        $user->save();
        $user->load('role');
        return response()->json(['success'=>true, 'data'=>$user]);
    }
    
    public function update(Request $request, User $user) {
        $data = $request->validate([
              "role_id" => "required"
        ]);
        
        $user->update($data);
        
        return response()->json(['success' => true, 'data' => $user], 200);
    }

    public function revokeAdmin(User $user)
    {
        // возвращаем в «client» (ID = 1)
        $user->role_id = Role::where('name','client')->first()->id;
        $user->save();
        $user->load('role');
        return response()->json(['success'=>true, 'data'=>$user]);
    }
}
