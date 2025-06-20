# 1) Базовый образ с PHP и зависимостями
FROM php:8.2-fpm AS base

WORKDIR /var/www/html

# 1. Копируем только файлы зависимостей и ключевые скрипты
COPY composer.json composer.lock ./
COPY artisan ./
COPY bootstrap bootstrap/
COPY config config/
COPY routes routes/

# Устанавливаем системные пакеты и расширения
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       git zip unzip libpng-dev libonig-dev libxml2-dev \
    && docker-php-ext-install pdo_mysql mbstring exif pcntl bcmath gd \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Composer
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

# 2) Этап сборки зависимостей (vendor)
FROM base AS builder

WORKDIR /var/www/html

# Копируем только файлы зависимостей для кэша
COPY composer.json composer.lock ./

# Инсталлируем PHP-пакеты
RUN composer install --no-interaction --optimize-autoloader --no-dev

# 3) Финальный образ
FROM base AS final

WORKDIR /var/www/html

# Копируем vendor из builder
COPY --from=builder /var/www/html/vendor ./vendor

# Копируем весь код приложения
COPY . .

# Устанавливаем права
RUN chown -R www-data:www-data storage bootstrap/cache

EXPOSE 9000
CMD ["php-fpm"]
