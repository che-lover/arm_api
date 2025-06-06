<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('roles', function (Blueprint $table) {
            $table->id();
            $table->string('name')->unique();
            $table->string('display_name')->nullable();
            $table->timestamps();
        });

        \Illuminate\Support\Facades\DB::table('roles')->insert([
            ['id' => 1, 'name' => 'supervisor', 'display_name' => 'Супервайзер'],
            ['id' => 2, 'name' => 'admin', 'display_name' => 'Администратор'],
            ['id' => 3, 'name' => 'manager', 'display_name' => 'Менеджер'],
            ['id' => 4, 'name' => 'courier', 'display_name' => 'Курьер'],
            ['id' => 5, 'name' => 'client', 'display_name' => 'Клиент'],
        ]);
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('roles');
    }
};
