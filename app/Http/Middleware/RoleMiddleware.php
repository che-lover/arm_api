<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class RoleMiddleware
{
    /**
     * Handle an incoming request.
     *
     * @param  \Closure(\Illuminate\Http\Request): (\Symfony\Component\HttpFoundation\Response)  $next
     */
    public function handle(Request $request, Closure $next, ...$roles): Response
    {
        $user = $request->user();

        if (!$user) {
            return redirect()->json(['message' => 'Unauthenticated.'], 401);
        }

//        $allowedRoles = explode(',', $roles);
//        dd($user->role->name);
        
        if (! in_array($user->role->name, $roles, true)) {
            return response()->json(['message'=>'Forbidden.'], 403);
        }


        return $next($request);
    }
}
