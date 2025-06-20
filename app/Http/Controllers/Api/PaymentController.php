<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Coupon;
use App\Models\Inventory;
use App\Models\Order;
use App\Services\DashRpc;
use Illuminate\Http\Request;
use Carbon\Carbon;

class PaymentController extends Controller
{

    protected DashRpc $rpc;

    public function __construct(DashRpc $rpc)
    {
        $this->rpc = $rpc;
    }

    public function create(Request $request)
    {
        $data = $request->validate([
            'order_id' => 'required|integer|exists:orders,id',
            'coupon_id' => 'nullable',
            'apply_subscription_discount' => 'sometimes|boolean',
        ]);

        $order = Order::with(['items.packaging', 'coupon'])->findOrFail($data['order_id']);

        $totalLocal = $order->items->sum(function($item){
            return $item->quantity * $item->packaging->price;
        });

        if (! empty($data['coupon_id'])) {
            $coupon = Coupon::where('code', $data['coupon_id'])->first();

            if (! $coupon) {
            // купон не найден
            } else {
              $used = (bool) $coupon->used;
              $expiresAt = $coupon->expires_at
                ? Carbon::parse($coupon->expires_at)
                : null;

                if (! $used && (is_null($expiresAt) || $expiresAt->isFuture())) {
                  $pct = $coupon->discount_amount;
                    $totalLocal = $totalLocal * (100 - $pct) / 100;

                  $coupon->used = true;
                  $coupon->save();
                }
            }
        }

        if (! empty($data['apply_subscription_discount'])) {
            $totalLocal = max($totalLocal - 2, 0);
        }

        $dashRate   = config('dash.exchange_rate', 0.001);
        $amountDash = round($totalLocal * $dashRate, 8);

        $address = $this->rpc->getNewAddress((string)$order->id);
        $order->update([
            'payment_address' => $address,
            'amount_dash'     => $amountDash,
            'status'          => 'pending',
        ]);



        return response()->json([
            'success'         => true,
            'order_id' => $order->id,
            'payment_address' => $address,
            'amount_dash' => $order->amount_dash
        ], 200);
    }

//    public function status(Order $order)
//    {
//        $inv = null;
//        if (!$order->payment_address) {
//            return response()->json(['success' => false, 'error' => 'No payment address'], 404);
//        }
//
//        $received = $this->rpc->getReceivedByAddress($order->payment_address, 1);
//
//        if ($received >= $order->amount_dash && $order->status !== 'paid') {
//            $order->update([
//                'status' => 'paid',
//                'paid_at' => now(),
//            ]);
//
//            $item = $order->items()->firstOrFail();
//            $inv = Inventory::where('packaging_id', $item->packaging_id)
//                ->where('city_id', $order->city_id)
//                ->where('district_id', $order->district_id)
//                ->where('quantity', '>=', $item->quantity)
//                ->where('status', 'confirmed')
//                ->lockForUpdate()             // чтобы избежать гонок
//                ->firstOrFail();
//            $inv->quantity -= $item->quantity;
//
//            if ($inv->quantity <= 0) {
//                $inv->status = 'sold';
//            }
//
//            $inv->save();
//
//        }
//
//
//
//        return response()->json(['success' => true, 'data' => [
//            'order_id' => $order->id,
//            'received_dash' => $received,
//            'status' => $order->status,
//            'stash' => $inv,
//        ]]);
//    }
    public function status(Order $order)
    {
        if (!$order->payment_address) {
            return response()->json(['success' => false, 'error' => 'No payment address'], 404);
        }

        // 1) Считаем, сколько DASH пришло
        $received = $this->rpc->getReceivedByAddress($order->payment_address, 1);

        // 2) Берём связанный OrderItem и его inventory_id
        $item = $order->items()->firstOrFail();

        // 3) Загружаем сам Inventory сразу с packaging/city/district
        $inv = Inventory::with(['packaging', 'city', 'district'])
            ->lockForUpdate()          // чтобы никто не списал одновременно
            ->findOrFail($item->inventory_id);

        // 4) Если оплатили впервые — отмечаем заказ и списываем количество
        if ($received >= $order->amount_dash && $order->status !== 'paid') {
            $order->update([
                'status' => 'paid',
                'paid_at' => now(),
            ]);

            $inv->quantity -= $item->quantity;
            if ($inv->quantity <= 0) {
                $inv->status = 'sold';
            }
            $inv->save();
        }

        // 5) Всегда возвращаем этот же $inv как stash
        return response()->json([
            'success' => true,
            'data' => [
                'order_id' => $order->id,
                'received_dash' => $received,
                'status' => $order->status,
                'stash' => $inv,
            ],
        ], 200);
    }

    /**
     * Отправить DASH на произвольный адрес
     *
     * @route POST /api/v1/payments/send
     * @body-param to_address string  Целевой адрес
     * @body-param amount_dash numeric Сумма DASH
     */
    public function send(Request $request)
    {
        $data = $request->validate([
            'to_address' => 'required|string',
            'amount_dash' => 'required|numeric|min:0.0001',
        ]);

        $txid = $this->rpc->sendToAddress($data['to_address'], $data['amount_dash']);

        return response()->json([
            'success' => true,
            'txid' => $txid,
        ], 200);
    }

    public function balance()
    {
        $balance = $this->rpc->getBalance();
        return response()->json([
            'success' => true,
            'balance' => $balance,
        ], 200);
    }
}
