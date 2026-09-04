from fastapi_mail import (
    ConnectionConfig,
    FastMail,
    MessageSchema,
    MessageType,
)

from app.core.config import settings


mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,

    MAIL_PASSWORD=settings.MAIL_PASSWORD,

    MAIL_FROM=settings.MAIL_FROM,

    MAIL_PORT=settings.MAIL_PORT,

    MAIL_SERVER=settings.MAIL_SERVER,

    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,

    MAIL_STARTTLS=True,

    MAIL_SSL_TLS=False,

    USE_CREDENTIALS=True,
)


mail = FastMail(
    mail_config
)


async def send_seller_otp_email(
    email: str,
    seller_name: str,
    otp: str,
) -> None:

    html = f"""
    <!DOCTYPE html>

    <html>

    <head>

        <meta charset="UTF-8">

        <title>
            Verify Seller Account
        </title>

    </head>

    <body
        style="
            font-family: Arial, sans-serif;
            background: #f5f7f5;
            padding: 30px;
        "
    >

        <div
            style="
                max-width: 500px;
                margin: auto;
                background: white;
                padding: 30px;
                border-radius: 12px;
            "
        >

            <h2>
                Welcome to Sewa Foundation
            </h2>

            <p>
                Hello {seller_name},
            </p>

            <p>
                Thank you for creating your seller account.
                Please verify your email address using the
                OTP below.
            </p>

            <div
                style="
                    text-align: center;
                    margin: 30px 0;
                "
            >

                <span
                    style="
                        display: inline-block;
                        font-size: 32px;
                        font-weight: bold;
                        letter-spacing: 8px;
                        background: #f0f4ef;
                        padding: 15px 25px;
                        border-radius: 10px;
                    "
                >
                    {otp}
                </span>

            </div>

            <p>
                This OTP expires in
                {settings.SELLER_OTP_EXPIRE_MINUTES}
                minutes.
            </p>

            <p>
                If you did not create this account,
                you can safely ignore this email.
            </p>

            <hr>

            <p
                style="
                    color: #777;
                    font-size: 12px;
                "
            >
                Sewa Foundation
            </p>

        </div>

    </body>

    </html>
    """

    message = MessageSchema(
        subject="Verify your Sewa Foundation seller account",

        recipients=[
            email
        ],

        body=html,

        subtype=MessageType.html,
    )

    await mail.send_message(
        message
    )
    

async def send_buyer_otp_email(
    email: str,
    buyer_name: str,
    otp: str,
) -> None:

    html = f"""
    <!DOCTYPE html>

    <html>

    <head>

        <meta charset="UTF-8">

        <title>
            Verify Buyer Account
        </title>

    </head>

    <body
        style="
            font-family: Arial, sans-serif;
            background: #f5f7f5;
            padding: 30px;
        "
    >

        <div
            style="
                max-width: 500px;
                margin: auto;
                background: white;
                padding: 30px;
                border-radius: 12px;
            "
        >

            <h2>
                Welcome to Sewa Foundation
            </h2>

            <p>
                Hello {buyer_name},
            </p>

            <p>
                Thank you for creating your buyer account.
                Please verify your email address using the
                OTP below.
            </p>

            <div
                style="
                    text-align: center;
                    margin: 30px 0;
                "
            >

                <span
                    style="
                        display: inline-block;
                        font-size: 32px;
                        font-weight: bold;
                        letter-spacing: 8px;
                        background: #f0f4ef;
                        padding: 15px 25px;
                        border-radius: 10px;
                    "
                >
                    {otp}
                </span>

            </div>

            <p>
                This OTP expires in
                {settings.SELLER_OTP_EXPIRE_MINUTES}
                minutes.
            </p>

            <p>
                If you did not create this account,
                you can safely ignore this email.
            </p>

            <hr>

            <p
                style="
                    color: #777;
                    font-size: 12px;
                "
            >
                Sewa Foundation
            </p>

        </div>

    </body>

    </html>
    """

    message = MessageSchema(
        subject="Verify your Sewa Foundation buyer account",

        recipients=[
            email
        ],

        body=html,

        subtype=MessageType.html,
    )

    await mail.send_message(
        message
    )
