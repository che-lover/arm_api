<?php
return [
    'rpc_user' => env('DASH_RPC_USER', 'che'),
    'rpc_password' => env('DASH_RPC_PASSWORD', 'pass'),
    'rpc_host' => env('DASH_RPC_HOST', 'dashd-testnet'),
    'rpc_port' => env('DASH_RPC_PORT', '19998'),
    'wallet' => env('DASH_WALLET', 'test_wallet')
];
