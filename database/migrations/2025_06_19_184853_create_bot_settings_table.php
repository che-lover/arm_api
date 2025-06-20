<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
use Illuminate\Support\Facades\DB;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('bot_settings', function (Blueprint $table) {
            $table->id();
            $table->string('exchange_url')->nullable()->comment('Ссылка на обменник');
            $table->boolean('captcha_enabled')->default(true)->comment('Включена ли капча');
            $table->string('channel_link')->nullable()->comment('Ссылка на канал');
            $table->string('operator_contact')->nullable()->comment('Контакт оператора');
            $table->json('bots')->nullable()->comment('Доп. данные для управления ботами (json)');
            $table->timestamps();
        });
        
        DB::table('bot_settings')->insert([
            'captcha_enabled'   => true,
            'created_at'        => now(),
            'updated_at'        => now(),
        ]);
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('bot_settings');
    }
};
