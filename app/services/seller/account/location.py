from decimal import Decimal


def validate_coordinates(
        latitude: Decimal | None,
        longitude: Decimal | None,
    ) -> None:

        # Both must exist together
        if (
            latitude is None
            and longitude is None
        ):
            return

        if (
            latitude is None
            or longitude is None
        ):
            raise ValueError(
                "Latitude and longitude must be provided together."
            )

        if not (
            Decimal("-90")
            <= latitude
            <= Decimal("90")
        ):
            raise ValueError(
                "Invalid latitude."
            )

        if not (
            Decimal("-180")
            <= longitude
            <= Decimal("180")
        ):
            raise ValueError(
                "Invalid longitude."
            )


def validate_store_coordinates(
        latitude: Decimal,
        longitude: Decimal,
    ) -> None:

        if not (
            Decimal("-90")
            <= latitude
            <= Decimal("90")
        ):
            raise ValueError(
                "Invalid store latitude."
            )

        if not (
            Decimal("-180")
            <= longitude
            <= Decimal("180")
        ):
            raise ValueError(
                "Invalid store longitude."
            )