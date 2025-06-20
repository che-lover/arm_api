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
        Schema::table('orders', function (Blueprint $table) {
            $table->string('payment_address')->nullable()->after('status');
            $table->decimal('amount_dash', 16, 8)->nullable()->after('payment_address');
            $table->timestamp('paid_at')->nullable()->after('amount_dash');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('orders', function (Blueprint $table) {
            $table->dropColumn('payment_address');
            $table->dropColumn('amount_dash');
            $table->dropColumn('paid_at');
        });
    }
};
