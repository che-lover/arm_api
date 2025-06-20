<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class BotSetting extends Model
{
    protected $fillable = [
        'exchange_url',
        'captcha_enabled',
        'channel_link',
        'operator_contact',
        'bots',
    ];

    protected $casts = [
        'captcha_enabled' => 'boolean',
        'bots'            => 'array',
    ];
}
