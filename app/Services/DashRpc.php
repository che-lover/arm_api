<?php

namespace App\Services;

use GuzzleHttp\Client;

class DashRpc
{
    protected Client $http;

    public function __construct()
    {
        $this->http = new Client([
            'base_uri' => 'http://' . config('dash.rpc_host') . ':' . config('dash.rpc_port'),
            'auth' => [config('dash.rpc_user'), config('dash.rpc_password')],
            'timeout' => 5,
        ]);

//        $cfg = config('dash');

//        // Собираем URI вида http://user:pass@dashd-testnet:19998/wallet/test_wallet
//        $uri = sprintf(
//            'http://%s:%s@%s:%d/wallet/%s',
//            $cfg['rpc_user'],
//            $cfg['rpc_password'],
//            $cfg['rpc_host'],
//            $cfg['rpc_port'],
//            $cfg['wallet']
//        );

//        $this->http = new Client([
//            'base_uri' => $uri . '/',
//            'timeout'  => 5,
//        ]);
    }

    protected function call(string $method, array $params = [])
    {
        $response = $this->http->post('', [
            'json' => [
                'jsonrpc' => '1.0',
                'id' => 'laravel',
                'method' => $method,
                'params' => $params
            ],
        ]);

        $body = json_decode((string)$response->getBody(), true);

        if (isset($body['error']) && $body['error'] != null) {
            throw new \RuntimeException("RPC error: " . json_encode($body['error']));
        }

        return $body['result'];
    }

    public function getNewAddress(string $label = ''): string
    {
        return $this->call('getnewaddress', [$label]);
    }

    public function getReceivedByAddress(string $address, int $minConf = 1): float
    {
        return (float)$this->call('getreceivedbyaddress', [$address, $minConf]);
    }

    public function getBalance(): float
    {
        return (float)$this->call('getbalance');
    }
    
     /**
     * Отправить DASH на произвольный адрес
     *
     * @param  string  $address
     * @param  float   $amount
     * @return string  txid транзакции
     */
    
    public function sendToAddress(string $address, float $amount): string
    {
        // метод JSON-RPC dashd: sendtoaddress
        return (string)$this->call('sendtoaddress', [$address, $amount]);
    }

}
