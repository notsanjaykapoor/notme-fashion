import os

import sentry_sdk
import sentry_sdk.integrations.fastapi
import sentry_sdk.integrations.starlette


def init():
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        environment=os.getenv("APP_ENV"),
        # Add data like request headers and IP for users,
        # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
        send_default_pii=True,
        integrations=[
            sentry_sdk.integrations.starlette.StarletteIntegration(
                transaction_style="endpoint",
                failed_request_status_codes={*range(400, 599)},
                # http_methods_to_capture=("GET",),
            ),
            sentry_sdk.integrations.fastapi.FastApiIntegration(
                transaction_style="endpoint",
                failed_request_status_codes={*range(400, 599)},
                # http_methods_to_capture=("GET",),
            ),
        ],
        # Set traces_sample_rate to 1.0 to capture 100% of transactions for tracing.
        traces_sample_rate=1.0,
    )