from app.core.config import settings

from fastapi_mail import FastMail, MessageSchema, MessageType,ConnectionConfig
from pydantic import EmailStr


    # MAIL_USERNAME: str = "2634808@leapmotor.com"
    # # 邮箱授权码（不是登录密码！）
    # MAIL_PASSWORD: str = "Sqy123456."
    # # 发件人邮箱
    # MAIL_FROM: str = "shang_qingyuan@leapmotor.com"
    # # 发件人名称
    # MAIL_FROM_NAME: str = "自动化测试平台官方"
    # # SMTP 服务器地址
    # MAIL_SERVER: str = "mail.leapmotor.com"
    # # 邮箱是否需要 STARTTLS 加密
    # MAIL_STARTTLS: bool = True,
    # # 邮箱是否需要 SSL 加密
    # MAIL_SSL_TLS: bool = False,
    # # 邮箱是否需要验证证书
    # VALIDATE_CERTS: bool = True,
    # # 邮箱是否需要使用认证
    # USE_CREDENTIALS: bool = True,
    # # SMTP 端口（465 是 SSL 安全端口）
    # MAIL_PORT: int = 587

conf = ConnectionConfig(

    MAIL_USERNAME=settings.MAIL_USERNAME,
    # 邮箱授权码（不是登录密码！）
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    # 发件人邮箱
    MAIL_FROM=settings.MAIL_FROM,
    # 发件人名称
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    # SMTP 服务器地址
    MAIL_SERVER=settings.MAIL_SERVER,  # QQ邮箱用这个
    # MAIL_SERVER="smtp.163.com",  # 163邮箱用这个
    # SMTP 端口（465 是 SSL 安全端口，几乎通用）
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
)


# 3. 发送普通文本邮件接口
async def send_text_email(
    to_email: EmailStr,  # 收件人邮箱
    subject: str = "测试",  # 邮件标题
    body: str = "da"  # 邮件内容
):
    subject = "忘记密码邮件"

    # 构造邮件消息
    message = MessageSchema(
        subject=subject,
        recipients=[to_email],  # 收件人列表
        body=body,
        subtype=MessageType.plain  # 纯文本
    )

    # 发送邮件
    fm = FastMail(conf)
    await fm.send_message(message)
    return {"code":200 , "msg": "邮件发送成功！","data":None}