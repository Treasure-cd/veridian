-- Tracking promotions across products
CREATE TABLE promotions (
    promotion_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id      UUID NOT NULL REFERENCES product_service_catalogue(product_id),
    discount_type   VARCHAR(20) NOT NULL
                    CHECK (discount_type IN ('percentage','fixed_amount','bogo')),
    start_date       DATE NOT NULL,
    end_date         DATE NOT NULL,
    CHECK (end_date > start_date)
);
